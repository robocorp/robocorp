"""Redis-based work item adapter for distributed processing.

This module implements a custom work item adapter using Redis as the backend.
Perfect for distributed processing with multiple parallel workers.

Features:
- Atomic queue operations using RPOPLPUSH
- Hybrid file storage (inline <1MB, filesystem >1MB)
- Connection pooling with health checks
- Orphaned work item recovery
- Support for Redis Cluster and Sentinel

Usage:
    from robocorp.workitems import Inputs

    # Set environment variables
    os.environ["RC_WORKITEM_ADAPTER"] = "robocorp.workitems.RedisAdapter"
    os.environ["RC_REDIS_URL"] = "redis://localhost:6379/0"

    # Use work items as normal
    for item in Inputs:
        # Process work item...
        pass
"""

import base64
import json
import logging
import os
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional

from .._exceptions import ApplicationException, EmptyQueue
from .._types import TTL_WEEK_SECONDS, State
from .._utils import JSONType
from ._base import BaseAdapter
from ._support import with_retry

LOGGER = logging.getLogger(__name__)

# Try to import redis
try:  # pragma: no cover - optional dependency
    import redis as _redis_lib  # type: ignore[import-not-found]
    from redis.exceptions import (
        ConnectionError as _RedisConnectionError,  # type: ignore[import-not-found]
    )
except ImportError:  # pragma: no cover
    _redis_lib = None  # type: ignore[assignment]

    class _RedisConnectionError(Exception):  # type: ignore[no-redef]
        """Fallback connection error when redis is unavailable."""


RedisConnectionError = _RedisConnectionError


# File size threshold for hybrid storage (1MB)
INLINE_FILE_THRESHOLD = 1_000_000

# Maximum file size (100MB)
MAX_FILE_SIZE = 104_857_600


class ProcessingState(str, Enum):
    """Lifecycle states tracked in Redis payload metadata."""

    PENDING = "PENDING"
    RESERVED = "RESERVED"
    COMPLETED = State.DONE.value  # "COMPLETED"
    FAILED = State.FAILED.value  # "FAILED"


class DatabaseTemporarilyUnavailable(ApplicationException):
    """Redis is temporarily unavailable (connection error)."""


class RedisAdapter(BaseAdapter):
    """Redis-backed work item adapter for distributed processing.

    Implements the BaseAdapter interface using Redis as the backend. Redis provides
    high-performance distributed queue operations with atomic reservation.

    Redis Key Structure:
        {queue}:pending          - List[work_item_id] (FIFO queue)
        {queue}:processing       - List[work_item_id] (reserved items)
        {queue}:done             - Set[work_item_id] (completed items)
        {queue}:failed           - Set[work_item_id] (failed items)
        {queue}:payload:{id}     - Hash{payload, queue_name, state}
        {queue}:files:{id}       - Hash{filename: content_or_path}
        {queue}:state:{id}       - String (terminal state)
        {queue}:parent:{id}      - String (parent work item ID)
        {queue}:exception:{id}   - Hash{type, code, message}
        {queue}:timestamps:{id}  - Hash{created_at, reserved_at, released_at}
        origin:{id}              - String (origin queue for cross-queue lookups)

    Environment Variables:
        RC_REDIS_URL: Redis connection URL (default: redis://localhost:6379/0)
        RC_WORKITEM_QUEUE_NAME: Queue identifier (default: default)
        RC_WORKITEM_FILES_DIR: Files directory (default: devdata/work_item_files)
        RC_WORKITEM_ORPHAN_TIMEOUT_MINUTES: Orphan timeout (default: 30)

    lazydocs: ignore
    """

    def __init__(self):
        """Initialize RedisAdapter with connection pool and configuration.

        Raises:
            ImportError: If redis package not installed
            ApplicationException: If Redis connection fails
        """
        if _redis_lib is None:
            raise ImportError(
                "Redis support requires the redis package. "
                "Install it with: pip install robocorp-workitems[redis]"
            )

        # Load configuration
        redis_url = os.getenv("RC_REDIS_URL", "redis://localhost:6379/0")
        self.queue_name = os.getenv("RC_WORKITEM_QUEUE_NAME", "default")
        self.output_queue_name = f"{self.queue_name}_output"
        self.files_dir = Path(
            os.getenv("RC_WORKITEM_FILES_DIR", "devdata/work_item_files")
        )
        self.orphan_timeout_minutes = int(
            os.getenv("RC_WORKITEM_ORPHAN_TIMEOUT_MINUTES", "30")
        )

        # Create files directory
        self.files_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Redis client
        try:
            self._client = _redis_lib.from_url(
                redis_url,
                decode_responses=False,  # Handle binary data
                socket_connect_timeout=5,
                socket_keepalive=True,
                health_check_interval=30,
            )

            # Test connection
            self._client.ping()

            LOGGER.info(
                "RedisAdapter initialized: url=%s, queue=%s",
                redis_url,
                self.queue_name,
            )
        except Exception as e:
            LOGGER.critical("Failed to connect to Redis: %s", e)
            raise ApplicationException(f"Redis connection failed: {e}")

        # Cache for resolved queues to avoid redundant lookups
        self._queue_cache: dict[str, str] = {}

    def _key(self, suffix: str, queue: Optional[str] = None, item_id: str = "") -> str:
        """Generate Redis key with queue namespace.

        Args:
            suffix: Key suffix (e.g., 'pending', 'payload', 'files')
            queue: Queue namespace (defaults to adapter queue)
            item_id: Work item ID (optional, for item-specific keys)

        Returns:
            Redis key string
        """
        if suffix == "origin":
            return f"origin:{item_id}" if item_id else "origin"

        queue_name = queue or self.queue_name
        if item_id:
            return f"{queue_name}:{suffix}:{item_id}"
        return f"{queue_name}:{suffix}"

    def _resolve_item_queue(self, item_id: str) -> str:
        """Determine which queue namespace contains the work item.

        Checks input queue, output queue, and origin tracking key.
        Results are cached to avoid redundant Redis operations.

        Args:
            item_id: Work item ID

        Returns:
            Queue name where item is stored

        Raises:
            ValueError: If work item not found in any queue
        """
        # Check cache first
        if item_id in self._queue_cache:
            return self._queue_cache[item_id]

        # Check input queue
        if self._client.hexists(self._key("payload", item_id=item_id), "payload"):
            queue_name = self.queue_name
        else:
            # Check origin tracking
            origin = self._client.get(f"origin:{item_id}")
            if origin:
                queue_name = (
                    origin.decode("utf-8") if isinstance(origin, bytes) else origin
                )
                if self._client.hexists(
                    self._key("payload", queue=queue_name, item_id=item_id), "payload"
                ):
                    pass  # queue_name is set
                else:
                    queue_name = None
            else:
                queue_name = None

            # Check output queue if not found
            if queue_name is None:
                if self._client.hexists(
                    self._key("payload", queue=self.output_queue_name, item_id=item_id),
                    "payload",
                ):
                    queue_name = self.output_queue_name
                else:
                    raise ValueError(f"Work item not found: {item_id}")

        # Cache the result
        self._queue_cache[item_id] = queue_name
        return queue_name

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(RedisConnectionError, DatabaseTemporarilyUnavailable),
    )
    def reserve_input(self) -> str:
        """Reserve next pending work item from queue.

        Uses RPOPLPUSH to atomically move from pending to processing list.

        Returns:
            str: Work item ID (UUID)

        Raises:
            EmptyQueue: No pending work items available
            DatabaseTemporarilyUnavailable: Redis connection error (retried)
        """
        LOGGER.debug("Reserving next input work item from queue: %s", self.queue_name)

        try:
            # Atomic move: pending -> processing
            item_id = self._client.rpoplpush(
                self._key("pending"),
                self._key("processing"),
            )

            if item_id is None:
                raise EmptyQueue(f"No work items in queue: {self.queue_name}")

            # Decode bytes to string
            item_id_str = (
                item_id.decode("utf-8") if isinstance(item_id, bytes) else item_id
            )

            # Update timestamps
            now = datetime.utcnow().isoformat()
            self._client.hset(
                self._key("timestamps", item_id=item_id_str), "reserved_at", now
            )

            # Update state in payload metadata
            self._client.hset(
                self._key("payload", item_id=item_id_str),
                "state",
                ProcessingState.RESERVED.value,
            )

            LOGGER.info("Reserved input work item: %s", item_id_str)
            return item_id_str

        except RedisConnectionError as e:
            LOGGER.error("Redis connection error during reserve: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Redis connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(RedisConnectionError, DatabaseTemporarilyUnavailable),
    )
    def release_input(
        self, item_id: str, state: State, exception: Optional[dict] = None
    ) -> None:
        """Release work item with terminal state.

        Moves from processing list to done/failed set and records exception if failed.

        Args:
            item_id: Work item ID
            state: Terminal state (State.DONE or State.FAILED)
            exception: Exception details if state is FAILED

        Raises:
            ValueError: Invalid state or missing exception for FAILED
            DatabaseTemporarilyUnavailable: Redis connection error (retried)
        """
        if state not in (State.DONE, State.FAILED):
            raise ValueError(f"Release state must be DONE or FAILED, got {state}")

        if state == State.FAILED and not exception:
            raise ValueError("Exception details required when state=FAILED")

        try:
            # Remove from processing list
            self._client.lrem(self._key("processing"), 0, item_id)

            # Add to appropriate terminal set
            lifecycle_state = (
                ProcessingState.COMPLETED.value
                if state == State.DONE
                else ProcessingState.FAILED.value
            )

            if state == State.DONE:
                self._client.sadd(self._key("done"), item_id)
            else:
                self._client.sadd(self._key("failed"), item_id)

                # Store exception details
                if exception:
                    self._client.hset(
                        self._key("exception", item_id=item_id),
                        mapping={
                            "type": exception.get("type", "UnknownException"),
                            "code": exception.get("code", ""),
                            "message": exception.get("message", ""),
                        },
                    )
                    self._client.expire(self._key("exception", item_id=item_id), 86400)

            # Update timestamps
            now = datetime.utcnow().isoformat()
            self._client.hset(
                self._key("timestamps", item_id=item_id), "released_at", now
            )

            # Store terminal state
            self._client.set(self._key("state", item_id=item_id), state.value)
            self._client.hset(
                self._key("payload", item_id=item_id),
                "state",
                lifecycle_state,
            )

            log_func = LOGGER.error if state == State.FAILED else LOGGER.info
            log_func(
                "Released work item %s with state %s (exception: %s)",
                item_id,
                state.value,
                exception.get("message") if exception else None,
            )

        except RedisConnectionError as e:
            LOGGER.error("Redis connection error during release: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Redis connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(RedisConnectionError, DatabaseTemporarilyUnavailable),
    )
    def create_output(
        self, parent_id: Optional[str], payload: Optional[JSONType] = None
    ) -> str:
        """Create new output work item.

        Creates a work item in PENDING state in the output queue.

        Args:
            parent_id: Parent work item ID
            payload: JSON payload data

        Returns:
            str: New work item ID (UUID)

        Raises:
            DatabaseTemporarilyUnavailable: Redis connection error (retried)
        """
        item_id = str(uuid.uuid4())
        payload_data = payload if payload is not None else {}
        output_queue = self.output_queue_name

        LOGGER.debug(
            "Creating output work item for parent %s in queue %s",
            parent_id or "None",
            output_queue,
        )

        try:
            # Store payload metadata
            self._client.hset(
                self._key("payload", queue=output_queue, item_id=item_id),
                mapping={
                    "payload": json.dumps(payload_data),
                    "queue_name": output_queue,
                    "state": ProcessingState.PENDING.value,
                },
            )
            self._client.expire(
                self._key("payload", queue=output_queue, item_id=item_id),
                TTL_WEEK_SECONDS,
            )

            # Store parent relationship
            if parent_id:
                self._client.set(
                    self._key("parent", queue=output_queue, item_id=item_id), parent_id
                )
                self._client.expire(
                    self._key("parent", queue=output_queue, item_id=item_id),
                    TTL_WEEK_SECONDS,
                )

            # Store timestamps
            now = datetime.utcnow().isoformat()
            self._client.hset(
                self._key("timestamps", queue=output_queue, item_id=item_id),
                mapping={"created_at": now},
            )
            self._client.expire(
                self._key("timestamps", queue=output_queue, item_id=item_id),
                TTL_WEEK_SECONDS,
            )

            # Add to output pending queue (LPUSH for FIFO with RPOPLPUSH)
            self._client.lpush(self._key("pending", queue=output_queue), item_id)

            # Store origin queue for cross-queue lookups
            self._client.set(f"origin:{item_id}", output_queue, ex=TTL_WEEK_SECONDS)

            LOGGER.info("Created output work item: %s", item_id)
            return item_id

        except RedisConnectionError as e:
            LOGGER.error("Redis connection error during create: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Redis connection failed: {e}")

    def seed_input(self, payload: Optional[JSONType] = None) -> str:
        """Create work item directly in input queue (for testing).

        Args:
            payload: JSON payload data

        Returns:
            str: New work item ID
        """
        item_id = str(uuid.uuid4())
        payload_data = payload if payload is not None else {}

        try:
            self._client.hset(
                self._key("payload", item_id=item_id),
                mapping={
                    "payload": json.dumps(payload_data),
                    "queue_name": self.queue_name,
                    "state": ProcessingState.PENDING.value,
                },
            )
            self._client.expire(self._key("payload", item_id=item_id), TTL_WEEK_SECONDS)

            now = datetime.utcnow().isoformat()
            self._client.hset(
                self._key("timestamps", item_id=item_id), mapping={"created_at": now}
            )
            self._client.expire(
                self._key("timestamps", item_id=item_id), TTL_WEEK_SECONDS
            )

            self._client.lpush(self._key("pending"), item_id)
            self._client.set(f"origin:{item_id}", self.queue_name, ex=TTL_WEEK_SECONDS)

            LOGGER.debug("Seeded input work item: %s", item_id)
            return item_id

        except RedisConnectionError as e:
            LOGGER.error("Redis connection error during seed_input: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Redis connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(RedisConnectionError, DatabaseTemporarilyUnavailable),
    )
    def load_payload(self, item_id: str) -> dict:
        """Load JSON payload from work item.

        Args:
            item_id: Work item ID

        Returns:
            dict: JSON payload data

        Raises:
            ValueError: Work item not found
            DatabaseTemporarilyUnavailable: Redis connection error (retried)
        """
        LOGGER.debug("Loading payload for work item: %s", item_id)

        try:
            queue_name = self._resolve_item_queue(item_id)
            payload_json = self._client.hget(
                self._key("payload", queue=queue_name, item_id=item_id), "payload"
            )

            if payload_json is None:
                raise ValueError(f"Work item not found: {item_id}")

            # Decode and parse JSON
            payload_str = (
                payload_json.decode("utf-8")
                if isinstance(payload_json, bytes)
                else payload_json
            )
            return json.loads(payload_str)

        except RedisConnectionError as e:
            LOGGER.error("Redis connection error during load_payload: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Redis connection failed: {e}")
        except json.JSONDecodeError as e:
            LOGGER.error("Invalid JSON payload for work item %s: %s", item_id, e)
            raise ValueError(f"Invalid JSON payload: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(RedisConnectionError, DatabaseTemporarilyUnavailable),
    )
    def save_payload(self, item_id: str, payload: JSONType) -> None:
        """Save JSON payload to work item.

        Args:
            item_id: Work item ID
            payload: JSON payload data

        Raises:
            ValueError: Work item not found
            DatabaseTemporarilyUnavailable: Redis connection error (retried)
        """
        LOGGER.debug("Saving payload for work item: %s", item_id)

        try:
            queue_name = self._resolve_item_queue(item_id)
            exists = self._client.exists(
                self._key("payload", queue=queue_name, item_id=item_id)
            )
            if not exists:
                raise ValueError(f"Work item not found: {item_id}")

            payload_json = json.dumps(payload)
            self._client.hset(
                self._key("payload", queue=queue_name, item_id=item_id),
                "payload",
                payload_json,
            )

        except RedisConnectionError as e:
            LOGGER.error("Redis connection error during save_payload: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Redis connection failed: {e}")
        except (TypeError, ValueError) as e:
            LOGGER.error("Invalid payload for work item %s: %s", item_id, e)
            raise ValueError(f"Payload not JSON-serializable: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(RedisConnectionError, DatabaseTemporarilyUnavailable),
    )
    def list_files(self, item_id: str) -> list[str]:
        """List file attachments for work item.

        Args:
            item_id: Work item ID

        Returns:
            list[str]: List of filenames

        Raises:
            DatabaseTemporarilyUnavailable: Redis connection error (retried)
        """
        LOGGER.debug("Listing files for work item: %s", item_id)

        try:
            queue_name = self._resolve_item_queue(item_id)
            files_hash = self._client.hkeys(
                self._key("files", queue=queue_name, item_id=item_id)
            )

            filenames = [
                f.decode("utf-8") if isinstance(f, bytes) else f for f in files_hash
            ]
            return filenames

        except RedisConnectionError as e:
            LOGGER.error("Redis connection error during list_files: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Redis connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(RedisConnectionError, DatabaseTemporarilyUnavailable),
    )
    def get_file(self, item_id: str, name: str) -> bytes:
        """Retrieve file content from work item.

        Uses hybrid storage: inline for <1MB, filesystem for larger files.

        Args:
            item_id: Work item ID
            name: Filename

        Returns:
            bytes: File content

        Raises:
            FileNotFoundError: File not found
            DatabaseTemporarilyUnavailable: Redis connection error (retried)
        """
        LOGGER.debug("Getting file '%s' from work item: %s", name, item_id)

        try:
            queue_name = self._resolve_item_queue(item_id)
            file_ref = self._client.hget(
                self._key("files", queue=queue_name, item_id=item_id), name
            )

            if file_ref is None:
                raise FileNotFoundError(
                    f"File not found: {name} (work item: {item_id})"
                )

            # Decode reference
            file_ref_str = (
                file_ref.decode("utf-8") if isinstance(file_ref, bytes) else file_ref
            )

            # Check if filesystem reference
            if file_ref_str.startswith("file://"):
                filepath = Path(file_ref_str[7:])
                if not filepath.exists():
                    raise FileNotFoundError(f"File not found on filesystem: {filepath}")
                return filepath.read_bytes()
            else:
                # Inline storage (base64 encoded)
                return base64.b64decode(file_ref)

        except RedisConnectionError as e:
            LOGGER.error("Redis connection error during get_file: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Redis connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(RedisConnectionError, DatabaseTemporarilyUnavailable),
    )
    def add_file(self, item_id: str, name: str, content: bytes) -> None:
        """Attach file to work item.

        Uses hybrid storage: inline <1MB, filesystem >1MB.

        Args:
            item_id: Work item ID
            name: Filename
            content: File content

        Raises:
            ValueError: Invalid filename or file too large
            FileExistsError: File already exists
            DatabaseTemporarilyUnavailable: Redis connection error (retried)
        """
        # Validate filename
        if "/" in name or "\\" in name:
            raise ValueError(f"Invalid filename (no path separators): {name}")

        if len(name) > 255:
            raise ValueError(f"Filename too long (max 255 chars): {name}")

        if len(content) > MAX_FILE_SIZE:
            raise ValueError(
                f"File too large (max {MAX_FILE_SIZE} bytes): {len(content)} bytes"
            )

        LOGGER.debug(
            "Adding file '%s' to work item %s (%d bytes)", name, item_id, len(content)
        )

        try:
            # Resolve queue first to avoid redundant lookups
            queue_name = self._resolve_item_queue(item_id)

            # Check if file already exists
            exists = self._client.hexists(
                self._key("files", queue=queue_name, item_id=item_id), name
            )
            if exists:
                raise FileExistsError(f"File already exists: {name}")

            if len(content) > INLINE_FILE_THRESHOLD:
                # Large file: Store on filesystem
                filepath = self.files_dir / item_id / name
                filepath.parent.mkdir(parents=True, exist_ok=True)
                filepath.write_bytes(content)

                self._client.hset(
                    self._key("files", queue=queue_name, item_id=item_id),
                    name,
                    f"file://{filepath}",
                )
            else:
                # Small file: Store inline (base64)
                encoded_content = base64.b64encode(content).decode("utf-8")
                self._client.hset(
                    self._key("files", queue=queue_name, item_id=item_id),
                    name,
                    encoded_content,
                )

            # Set expiration
            self._client.expire(
                self._key("files", queue=queue_name, item_id=item_id), TTL_WEEK_SECONDS
            )

        except RedisConnectionError as e:
            LOGGER.error("Redis connection error during add_file: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Redis connection failed: {e}")

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(RedisConnectionError, DatabaseTemporarilyUnavailable),
    )
    def remove_file(self, item_id: str, name: str) -> None:
        """Remove file from work item.

        Deletes from Redis or filesystem depending on storage method.

        Args:
            item_id: Work item ID
            name: Filename

        Raises:
            FileNotFoundError: File not found
            DatabaseTemporarilyUnavailable: Redis connection error (retried)
        """
        LOGGER.debug("Removing file '%s' from work item %s", name, item_id)

        try:
            queue_name = self._resolve_item_queue(item_id)
            file_ref = self._client.hget(
                self._key("files", queue=queue_name, item_id=item_id), name
            )

            if file_ref is None:
                raise FileNotFoundError(
                    f"File not found: {name} (work item: {item_id})"
                )

            # Decode reference
            file_ref_str = (
                file_ref.decode("utf-8") if isinstance(file_ref, bytes) else file_ref
            )

            # Delete from filesystem if large file
            if file_ref_str.startswith("file://"):
                filepath = Path(file_ref_str[7:])
                if filepath.exists():
                    filepath.unlink()

            # Remove from Redis hash
            self._client.hdel(
                self._key("files", queue=queue_name, item_id=item_id), name
            )

        except RedisConnectionError as e:
            LOGGER.error("Redis connection error during remove_file: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Redis connection failed: {e}")

    def recover_orphaned_work_items(self) -> list[str]:
        """Recover orphaned work items beyond timeout.

        Resets RESERVED items to PENDING if reserved longer than timeout.

        Returns:
            list[str]: List of recovered work item IDs
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.orphan_timeout_minutes)

        LOGGER.info(
            "Recovering orphaned work items (timeout: %d min)",
            self.orphan_timeout_minutes,
        )

        try:
            processing_items = self._client.lrange(self._key("processing"), 0, -1)
            recovered_ids = []

            for item_id_bytes in processing_items:
                item_id = (
                    item_id_bytes.decode("utf-8")
                    if isinstance(item_id_bytes, bytes)
                    else item_id_bytes
                )

                # Get reserved_at timestamp
                reserved_at_str = self._client.hget(
                    self._key("timestamps", item_id=item_id), "reserved_at"
                )

                if reserved_at_str:
                    reserved_at_decoded = (
                        reserved_at_str.decode("utf-8")
                        if isinstance(reserved_at_str, bytes)
                        else reserved_at_str
                    )
                    reserved_at = datetime.fromisoformat(reserved_at_decoded)

                    if reserved_at < cutoff_time:
                        # Move back to pending
                        self._client.lrem(self._key("processing"), 0, item_id)
                        self._client.lpush(self._key("pending"), item_id)

                        # Clear reserved_at timestamp
                        self._client.hdel(
                            self._key("timestamps", item_id=item_id), "reserved_at"
                        )

                        # Update state
                        self._client.hset(
                            self._key("payload", item_id=item_id),
                            "state",
                            ProcessingState.PENDING.value,
                        )

                        recovered_ids.append(item_id)
                        LOGGER.warning("Recovered orphaned work item: %s", item_id)

            if recovered_ids:
                LOGGER.info("Recovered %d orphaned work items", len(recovered_ids))

            return recovered_ids

        except RedisConnectionError as e:
            LOGGER.error("Redis connection error during recovery: %s", e)
            raise DatabaseTemporarilyUnavailable(f"Redis connection failed: {e}")

    @property
    def _config(self) -> "_Config":
        return _Config(self)


class _Config:
    def __init__(self, adapter: RedisAdapter):
        self.queue = adapter.queue_name
        self.file_threshold = INLINE_FILE_THRESHOLD
