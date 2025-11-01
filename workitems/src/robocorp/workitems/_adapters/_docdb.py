"""DocumentDB-based work item adapter for MongoDB-compatible databases.

Features:
- MongoDB-wire protocol compatibility
- Collection-based work item storage with TTL indexes
- Connection pooling
- Orphaned work item recovery
- Atomic operations using findAndModify

Usage::

    from robocorp.workitems import Inputs

    # Set environment variables
    os.environ["RC_WORKITEM_ADAPTER"] = "robocorp.workitems.DocumentDBAdapter"
    os.environ["DOCDB_URI"] = "mongodb://localhost:27017"
    os.environ["DOCDB_DATABASE"] = "workitems"

    # Use work items as normal
    for item in Inputs:
        # Process work item...
        pass
"""

import base64
import hashlib
import logging
import os
import uuid
from collections.abc import Iterator, MutableMapping
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from .._exceptions import ApplicationException, EmptyQueue
from .._types import State
from .._utils import JSONType, required_env
from ._base import BaseAdapter
from ._support import with_retry

LOGGER = logging.getLogger(__name__)

# Try to import pymongo
try:  # pragma: no cover - optional dependency
    from gridfs import GridFS  # type: ignore[import-not-found]
    from pymongo import (  # type: ignore[import-not-found]
        ASCENDING,
        MongoClient,
        ReturnDocument,
    )
    from pymongo.errors import (
        ConnectionFailure as _ConnectionFailure,  # type: ignore[import-not-found]
    )
    from pymongo.errors import (
        OperationFailure as _OperationFailure,  # type: ignore[import-not-found]
    )

    _pymongo_available = True
except ImportError:  # pragma: no cover

    def _raise_pymongo_import_error(*args, **kwargs):
        raise ImportError(
            "DocumentDB support requires the pymongo package. "
            "Install it with: pip install robocorp-workitems[docdb]"
        )

    GridFS = _raise_pymongo_import_error  # type: ignore[assignment,misc]
    MongoClient = _raise_pymongo_import_error  # type: ignore[assignment,misc]
    ReturnDocument = _raise_pymongo_import_error  # type: ignore[assignment,misc]
    ASCENDING = _raise_pymongo_import_error  # type: ignore[assignment,misc]

    class _ConnectionFailure(Exception):  # type: ignore[no-redef]
        """Fallback connection failure when pymongo is unavailable."""

        def __init__(self, *args, **kwargs):
            _raise_pymongo_import_error()

    class _OperationFailure(Exception):  # type: ignore[no-redef]
        """Fallback operation failure when pymongo is unavailable."""

        def __init__(self, *args, **kwargs):
            _raise_pymongo_import_error()

    _pymongo_available = False


ConnectionFailure = _ConnectionFailure
OperationFailure = _OperationFailure

# File size threshold for GridFS (1MB)
GRIDFS_THRESHOLD = 1_000_000


class ProcessingState(str, Enum):
    """Lifecycle states tracked in DocumentDB collection."""

    PENDING = "PENDING"
    RESERVED = "RESERVED"
    COMPLETED = State.DONE.value  # "COMPLETED"
    FAILED = State.FAILED.value  # "FAILED"


class DatabaseTemporarilyUnavailable(ApplicationException):
    """Database is temporarily unavailable."""


class DocumentDBAdapter(BaseAdapter):
    """MongoDB/DocumentDB-backed work item adapter.

    Work Item Document Schema:
        {
            "_id": ObjectId("..."),
            "item_id": "uuid-string",
            "queue_name": "queue_name",
            "parent_id": "parent-uuid",
            "state": "PENDING|RESERVED|COMPLETED|FAILED",
            "payload": {...},
            "files": {
                "small_file.txt": "base64-content",
                "large_file.zip": {"gridfs_id": ObjectId(...)}
            },
            "exception": {"type": "...", "code": "...", "message": "..."},
            "timestamps": {
                "created_at": ISODate("..."),
                "reserved_at": ISODate("..."),
                "released_at": ISODate("...")
            }
        }

    Environment Variables:
        DOCDB_URI: MongoDB connection URI (required)
        DOCDB_DATABASE: Database name (required)
        RC_WORKITEM_QUEUE_NAME: Queue identifier (default: default)
        RC_WORKITEM_FILES_DIR: Files directory (default: devdata/work_item_files)
        RC_WORKITEM_ORPHAN_TIMEOUT_MINUTES: Orphan timeout (default: 30)

    lazydocs: ignore
    """

    def __init__(self):
        """Initialize DocumentDBAdapter.

        Raises:
            ImportError: If pymongo package not installed
            ApplicationException: If connection fails
        """
        if not _pymongo_available:
            raise ImportError(
                "DocumentDB support requires the pymongo package. "
                "Install it with: pip install robocorp-workitems[docdb]"
            )

        # Load configuration
        self.docdb_uri = required_env("DOCDB_URI")
        self.docdb_database = required_env("DOCDB_DATABASE")
        self.queue_name = os.getenv("RC_WORKITEM_QUEUE_NAME", "default")
        self.output_queue_name = f"{self.queue_name}_output"
        self.files_dir = Path(
            os.getenv("RC_WORKITEM_FILES_DIR", "devdata/work_item_files")
        )
        self.orphan_timeout_minutes = int(
            os.getenv("RC_WORKITEM_ORPHAN_TIMEOUT_MINUTES", "30")
        )
        self.file_threshold = int(
            os.getenv("RC_WORKITEM_FILE_SIZE_THRESHOLD", str(GRIDFS_THRESHOLD))
        )

        # Create files directory
        self.files_dir.mkdir(parents=True, exist_ok=True)

        # Initialize connection
        try:
            self._client = MongoClient(
                self.docdb_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                maxPoolSize=50,
            )

            # Test connection
            self._client.admin.command("ping")

            self._db = self._client[self.docdb_database]
            self._init_collections()

            LOGGER.info(
                "DocumentDBAdapter initialized: db=%s, queue=%s",
                self.docdb_database,
                self.queue_name,
            )
        except Exception as e:
            LOGGER.critical("Failed to connect to DocumentDB: %s", e)
            raise ApplicationException(f"DocumentDB connection failed: {e}")

    def _init_collections(self):
        """Initialize collections and indexes."""
        # Create indexes for input queue
        coll = self._collection()
        coll.create_index([("item_id", ASCENDING)], unique=True)
        coll.create_index(
            [
                ("queue_name", ASCENDING),
                ("state", ASCENDING),
                ("timestamps.created_at", ASCENDING),
            ]
        )

        # Create indexes for output queue
        output_coll = self._collection(queue=self.output_queue_name)
        output_coll.create_index([("item_id", ASCENDING)], unique=True)
        output_coll.create_index(
            [
                ("queue_name", ASCENDING),
                ("state", ASCENDING),
                ("timestamps.created_at", ASCENDING),
            ]
        )

        # Initialize GridFS
        self._gridfs = GridFS(self._db)

    def _collection(self, queue: Optional[str] = None):
        """Get collection for queue with document post-processing."""
        queue_name = queue or self.queue_name
        return _CollectionWrapper(self._db[f"{queue_name}_work_items"])

    @staticmethod
    def _make_file_key(name: str) -> str:
        return hashlib.sha1(name.encode("utf-8")).hexdigest()

    def _get_file_entry(
        self, doc: dict[str, Any], name: str
    ) -> tuple[str, dict[str, Any]]:
        files_dict = doc.get("files", {}) or {}

        if isinstance(files_dict, _FilesView):
            try:
                return files_dict.resolve(name)
            except KeyError as exc:
                raise FileNotFoundError(f"File not found: {name}") from exc

        if not isinstance(files_dict, dict):
            raise FileNotFoundError(f"File not found: {name}")

        if name in files_dict:
            value = files_dict[name]
            if isinstance(value, dict):
                entry = {"name": name, **value}
            else:
                entry = {"name": name, "storage": "inline", "content": value}
            return name, entry

        for key, entry in files_dict.items():
            if isinstance(entry, dict) and entry.get("name") == name:
                return key, entry

        raise FileNotFoundError(f"File not found: {name}")

    def _resolve_item_queue(self, item_id: str) -> str:
        """Find which queue contains the work item."""
        # Check input queue
        if self._collection().find_one({"item_id": item_id}):
            return self.queue_name

        # Check output queue
        if self._collection(queue=self.output_queue_name).find_one(
            {"item_id": item_id}
        ):
            return self.output_queue_name

        raise ValueError(f"Work item not found: {item_id}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(ConnectionFailure, DatabaseTemporarilyUnavailable),
    )
    def reserve_input(self) -> str:
        """Reserve next pending work item.

        Uses findAndModify for atomic reservation.

        Returns:
            str: Work item ID

        Raises:
            EmptyQueue: No pending work items available
        """
        LOGGER.debug("Reserving next input work item from queue: %s", self.queue_name)

        try:
            coll = self._collection()
            doc = coll.find_one_and_update(
                {"queue_name": self.queue_name, "state": ProcessingState.PENDING.value},
                {
                    "$set": {
                        "state": ProcessingState.RESERVED.value,
                        "timestamps.reserved_at": datetime.utcnow(),
                    }
                },
                sort=[("timestamps.created_at", ASCENDING)],
                return_document=ReturnDocument.AFTER,
            )

            if not doc:
                raise EmptyQueue(f"No work items in queue: {self.queue_name}")

            item_id = doc["item_id"]
            LOGGER.info("Reserved input work item: %s", item_id)
            return item_id

        except ConnectionFailure as e:
            LOGGER.error("MongoDB connection error: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(ConnectionFailure, DatabaseTemporarilyUnavailable),
    )
    def release_input(
        self, item_id: str, state: State, exception: Optional[dict] = None
    ) -> None:
        """Release work item with terminal state.

        Args:
            item_id: Work item ID
            state: Terminal state (State.DONE or State.FAILED)
            exception: Exception details if failed
        """
        if state not in (State.DONE, State.FAILED):
            raise ValueError(f"Release state must be DONE or FAILED, got {state}")

        if state == State.FAILED and not exception:
            raise ValueError("Exception details required when state=FAILED")

        try:
            coll = self._collection()
            update: dict[str, dict[str, Any]] = {
                "$set": {
                    "state": state.value,
                    "timestamps.released_at": datetime.utcnow(),
                }
            }

            if exception:
                update["$set"]["exception"] = exception

            coll.update_one({"item_id": item_id}, update)

            log_func = LOGGER.error if state == State.FAILED else LOGGER.info
            log_func(
                "Released work item %s with state %s",
                item_id,
                state.value,
            )

        except ConnectionFailure as e:
            LOGGER.error("MongoDB connection error: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(ConnectionFailure, DatabaseTemporarilyUnavailable),
    )
    def create_output(
        self, parent_id: Optional[str], payload: Optional[JSONType] = None
    ) -> str:
        """Create new output work item.

        Args:
            parent_id: Parent work item ID
            payload: JSON payload data

        Returns:
            str: New work item ID
        """
        item_id = str(uuid.uuid4())
        payload_data = payload if payload is not None else {}

        LOGGER.debug(
            "Creating output work item for parent %s in queue %s",
            parent_id or "None",
            self.output_queue_name,
        )

        try:
            coll = self._collection(queue=self.output_queue_name)
            doc = {
                "item_id": item_id,
                "queue_name": self.output_queue_name,
                "parent_id": parent_id,
                "state": ProcessingState.PENDING.value,
                "payload": payload_data,
                "files": {},
                "timestamps": {"created_at": datetime.utcnow()},
            }
            coll.insert_one(doc)

            LOGGER.info("Created output work item: %s", item_id)
            return item_id

        except ConnectionFailure as e:
            LOGGER.error("MongoDB connection error: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Connection failed: {e}")

    def seed_input(self, payload: Optional[JSONType] = None) -> str:
        """Create work item directly in input queue (for testing)."""
        item_id = str(uuid.uuid4())
        payload_data = payload if payload is not None else {}

        try:
            coll = self._collection()
            doc = {
                "item_id": item_id,
                "queue_name": self.queue_name,
                "parent_id": None,
                "state": ProcessingState.PENDING.value,
                "payload": payload_data,
                "files": {},
                "timestamps": {"created_at": datetime.utcnow()},
            }
            coll.insert_one(doc)

            LOGGER.debug("Seeded input work item: %s", item_id)
            return item_id

        except ConnectionFailure as e:
            LOGGER.error("MongoDB connection error: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(ConnectionFailure, DatabaseTemporarilyUnavailable),
    )
    def load_payload(self, item_id: str) -> dict:
        """Load JSON payload from work item.

        Args:
            item_id: Work item ID

        Returns:
            dict: JSON payload data

        Raises:
            ValueError: Work item not found
        """
        LOGGER.debug("Loading payload for work item: %s", item_id)

        try:
            queue_name = self._resolve_item_queue(item_id)
            coll = self._collection(queue=queue_name)
            doc = coll.find_one({"item_id": item_id})

            if not doc:
                raise ValueError(f"Work item not found: {item_id}")

            return doc.get("payload", {})

        except ConnectionFailure as e:
            LOGGER.error("MongoDB connection error: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(ConnectionFailure, DatabaseTemporarilyUnavailable),
    )
    def save_payload(self, item_id: str, payload: JSONType) -> None:
        """Save JSON payload to work item.

        Args:
            item_id: Work item ID
            payload: JSON payload data

        Raises:
            ValueError: Work item not found
        """
        LOGGER.debug("Saving payload for work item: %s", item_id)

        try:
            queue_name = self._resolve_item_queue(item_id)
            coll = self._collection(queue=queue_name)
            result = coll.update_one(
                {"item_id": item_id}, {"$set": {"payload": payload}}
            )

            if result.matched_count == 0:
                raise ValueError(f"Work item not found: {item_id}")

        except ConnectionFailure as e:
            LOGGER.error("MongoDB connection error: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(ConnectionFailure, DatabaseTemporarilyUnavailable),
    )
    def list_files(self, item_id: str) -> list[str]:
        """List file attachments for work item.

        Args:
            item_id: Work item ID

        Returns:
            list[str]: List of filenames
        """
        LOGGER.debug("Listing files for work item: %s", item_id)

        try:
            queue_name = self._resolve_item_queue(item_id)
            coll = self._collection(queue=queue_name)
            doc = coll.find_one({"item_id": item_id})

            if not doc:
                return []

            files_field = doc.get("files")
            if isinstance(files_field, _FilesView):
                return list(files_field)

            files_dict = files_field or {}
            if not isinstance(files_dict, dict):
                return []

            filenames: list[str] = []
            for key, entry in files_dict.items():
                if isinstance(entry, dict):
                    name = entry.get("name", key)
                    if name is not None:
                        filenames.append(name)
                else:
                    filenames.append(key)

            return filenames

        except ConnectionFailure as e:
            LOGGER.error("MongoDB connection error: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(ConnectionFailure, DatabaseTemporarilyUnavailable),
    )
    def get_file(self, item_id: str, name: str) -> bytes:
        """Retrieve file content from work item.

        Uses hybrid storage: inline for <1MB, GridFS for larger files.

        Args:
            item_id: Work item ID
            name: Filename

        Returns:
            bytes: File content

        Raises:
            FileNotFoundError: File not found
        """
        LOGGER.debug("Getting file '%s' from work item: %s", name, item_id)

        try:
            queue_name = self._resolve_item_queue(item_id)
            coll = self._collection(queue=queue_name)
            doc = coll.find_one({"item_id": item_id})

            if doc is None:
                raise ValueError(f"Work item not found: {item_id}")

            try:
                _, file_entry = self._get_file_entry(doc, name)
            except FileNotFoundError as exc:
                raise FileNotFoundError(
                    f"File not found: {name} (work item: {item_id})"
                ) from exc

            storage = file_entry.get("storage")
            if storage == "gridfs":
                gridfs_id = file_entry.get("gridfs_id")
                if gridfs_id is None:
                    raise FileNotFoundError(
                        f"GridFS reference missing for file: {name} (work item: {item_id})"
                    )
                gridfs_file = self._gridfs.get(gridfs_id)
                return gridfs_file.read()

            if storage == "inline":
                encoded = file_entry.get("content")
                if encoded is None:
                    raise FileNotFoundError(
                        f"Inline content missing for file: {name} (work item: {item_id})"
                    )
                return base64.b64decode(encoded)

            raise FileNotFoundError(f"File not found: {name} (work item: {item_id})")

        except ConnectionFailure as e:
            LOGGER.error("MongoDB connection error: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(ConnectionFailure, DatabaseTemporarilyUnavailable),
    )
    def add_file(self, item_id: str, name: str, content: bytes) -> None:
        """Attach file to work item.

        Uses hybrid storage: inline <1MB, GridFS >1MB.

        Args:
            item_id: Work item ID
            name: Filename
            content: File content

        Raises:
            FileExistsError: File already exists
        """
        LOGGER.debug(
            "Adding file '%s' to work item %s (%d bytes)", name, item_id, len(content)
        )

        try:
            queue_name = self._resolve_item_queue(item_id)
            coll = self._collection(queue=queue_name)
            doc = coll.find_one({"item_id": item_id})

            if not doc:
                raise ValueError(f"Work item not found: {item_id}")

            files_field = doc.get("files")
            if isinstance(files_field, _FilesView):
                if name in files_field:
                    raise FileExistsError(f"File already exists: {name}")
            else:
                files_dict = files_field or {}
                if not isinstance(files_dict, dict):
                    files_dict = {}

                if any(
                    (entry.get("name") == name)
                    if isinstance(entry, dict)
                    else key == name
                    for key, entry in files_dict.items()
                ):
                    raise FileExistsError(f"File already exists: {name}")

            file_key = self._make_file_key(name)
            if len(content) > self.file_threshold:
                gridfs_id = self._gridfs.put(content, filename=name)
                file_entry = {
                    "name": name,
                    "storage": "gridfs",
                    "gridfs_id": gridfs_id,
                }
            else:
                file_entry = {
                    "name": name,
                    "storage": "inline",
                    "content": base64.b64encode(content).decode("utf-8"),
                }

            coll.update_one(
                {"item_id": item_id},
                {"$set": {f"files.{file_key}": file_entry}},
            )

        except ConnectionFailure as e:
            LOGGER.error("MongoDB connection error: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(ConnectionFailure, DatabaseTemporarilyUnavailable),
    )
    def remove_file(self, item_id: str, name: str) -> None:
        """Remove file from work item.

        Deletes from GridFS or inline storage.

        Args:
            item_id: Work item ID
            name: Filename

        Raises:
            FileNotFoundError: File not found
        """
        LOGGER.debug("Removing file '%s' from work item %s", name, item_id)

        try:
            queue_name = self._resolve_item_queue(item_id)
            coll = self._collection(queue=queue_name)
            doc = coll.find_one({"item_id": item_id})

            if doc is None:
                raise ValueError(f"Work item not found: {item_id}")

            try:
                file_key, file_entry = self._get_file_entry(doc, name)
            except FileNotFoundError as exc:
                raise FileNotFoundError(
                    f"File not found: {name} (work item: {item_id})"
                ) from exc

            storage = file_entry.get("storage")
            if storage is None and "gridfs_id" in file_entry:
                storage = "gridfs"

            if storage == "gridfs" and "gridfs_id" in file_entry:
                self._gridfs.delete(file_entry["gridfs_id"])

            coll.update_one({"item_id": item_id}, {"$unset": {f"files.{file_key}": ""}})

        except ConnectionFailure as e:
            LOGGER.error("MongoDB connection error: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Connection failed: {e}")

    def recover_orphaned_work_items(self) -> list[str]:
        """Recover orphaned work items beyond timeout.

        Returns:
            list[str]: List of recovered work item IDs
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.orphan_timeout_minutes)

        LOGGER.info(
            "Recovering orphaned work items (timeout: %d min)",
            self.orphan_timeout_minutes,
        )

        try:
            coll = self._collection()
            result = coll.update_many(
                {
                    "state": ProcessingState.RESERVED.value,
                    "timestamps.reserved_at": {"$lt": cutoff_time},
                },
                {
                    "$set": {"state": ProcessingState.PENDING.value},
                    "$unset": {"timestamps.reserved_at": ""},
                },
            )

            if result.modified_count > 0:
                LOGGER.warning(
                    "Recovered %d orphaned work items", result.modified_count
                )

            return []  # DocumentDB doesn't easily return affected IDs

        except ConnectionFailure as e:
            LOGGER.error("MongoDB connection error: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Connection failed: {e}")

    @property
    def _config(self) -> "_Config":
        return _Config(self)


class _CollectionWrapper:
    """Wrap PyMongo collections to expose processed documents."""

    def __init__(self, collection: Any):
        self._collection = collection

    def find_one(self, *args, **kwargs):
        doc = self._collection.find_one(*args, **kwargs)
        return self._transform(doc)

    def find_one_and_update(self, *args, **kwargs):
        doc = self._collection.find_one_and_update(*args, **kwargs)
        return self._transform(doc)

    def _transform(self, doc: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
        if doc is None:
            return None

        processed = dict(doc)
        files = processed.get("files")
        if isinstance(files, dict):
            processed["files"] = _FilesView(files)

        return processed

    def __getattr__(self, name: str):
        return getattr(self._collection, name)


class _FilesView(MutableMapping[str, Any]):
    """Read-only mapping that exposes file metadata by original filename."""

    def __init__(self, raw: dict[str, Any]):
        self._raw = raw or {}

    def __getitem__(self, key: str) -> Any:
        _, entry = self.resolve(key)
        storage = entry.get("storage")
        if storage == "gridfs":
            return {"gridfs_id": entry.get("gridfs_id")}
        if storage == "inline":
            return entry.get("content")
        return entry

    def __setitem__(
        self, key: str, value: Any
    ) -> None:  # pragma: no cover - read-only view
        raise TypeError("Files view is read-only")

    def __delitem__(self, key: str) -> None:  # pragma: no cover - read-only view
        raise TypeError("Files view is read-only")

    def __iter__(self) -> Iterator[str]:
        yielded: set[str] = set()
        for raw_key, entry in self._raw.items():
            if isinstance(entry, dict) and "name" in entry:
                name = entry["name"]
            else:
                name = raw_key
            if name not in yielded:
                yielded.add(name)
                yield name

    def __len__(self) -> int:
        return sum(1 for _ in self.__iter__())

    def resolve(self, name: str) -> tuple[str, dict[str, Any]]:
        raw_key, entry = self._resolve(name)
        if not isinstance(entry, dict):
            entry = {"name": name, "storage": "inline", "content": entry}
        else:
            entry = dict(entry)
            entry.setdefault("name", name)
        return raw_key, entry

    def _resolve(self, name: str) -> tuple[str, Any]:
        for raw_key, entry in self._raw.items():
            if isinstance(entry, dict) and entry.get("name") == name:
                return raw_key, entry
        if name in self._raw:
            return name, self._raw[name]
        hashed = hashlib.sha1(name.encode("utf-8")).hexdigest()
        if hashed in self._raw:
            return hashed, self._raw[hashed]
        raise KeyError(name)


class _Config:
    def __init__(self, adapter: "DocumentDBAdapter"):
        self.queue = adapter.queue_name
        self.file_threshold = adapter.file_threshold
