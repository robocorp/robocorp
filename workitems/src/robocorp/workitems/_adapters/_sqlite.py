"""SQLite-based work item adapter.

This module implements a custom work item adapter using SQLite as the backend.
Perfect for local development and small-scale deployments.

Features:
- ACID transactions
- Concurrent read access (WAL mode)
- Filesystem-based file storage
- Automatic schema migrations
- Orphaned work item recovery

Usage:
    from robocorp.workitems import Inputs

    # Set environment variables
    os.environ["RC_WORKITEM_ADAPTER"] = "robocorp.workitems.SQLiteAdapter"
    os.environ["RC_WORKITEM_DB_PATH"] = "devdata/work_items.db"

    # Use work items as normal
    for item in Inputs:
        # Process work item...
        pass
"""

import json
import logging
import os
import sqlite3
import uuid
from enum import Enum
from pathlib import Path
from typing import Optional

from .._exceptions import ApplicationException, EmptyQueue
from .._types import State
from .._utils import JSONType, required_env
from ._base import BaseAdapter
from ._support import ThreadLocalConnectionPool, with_retry

LOGGER = logging.getLogger(__name__)

# Current schema version
SCHEMA_VERSION = 4


class ProcessingState(str, Enum):
    """Lifecycle states persisted in the SQLite work_items table."""

    PENDING = "PENDING"
    RESERVED = "RESERVED"
    COMPLETED = State.DONE.value  # "COMPLETED"
    FAILED = State.FAILED.value  # "FAILED"


_STATE_VALUES = (
    ProcessingState.PENDING.value,
    ProcessingState.RESERVED.value,
    ProcessingState.COMPLETED.value,
    ProcessingState.FAILED.value,
)

_STATE_VALUES_FOR_CHECK = ", ".join(f"'{value}'" for value in _STATE_VALUES)


class DatabaseTemporarilyUnavailable(ApplicationException):
    """Database is temporarily unavailable (locked or timed out)."""


class SQLiteAdapter(BaseAdapter):
    """SQLite-based work item adapter.

    This adapter stores work items in a SQLite database with support for:
    - Atomic work item reservation (PENDING → RESERVED)
    - State transitions (RESERVED → COMPLETED/FAILED)
    - JSON payload storage
    - File attachments (filesystem)
    - Automatic schema migrations
    - Orphaned work item recovery

    Environment Variables:
        RC_WORKITEM_DB_PATH: Path to SQLite database file (required)
        RC_WORKITEM_FILES_DIR: Directory for file attachments (default: devdata/work_item_files)
        RC_WORKITEM_QUEUE_NAME: Queue identifier (default: default)
        RC_WORKITEM_ORPHAN_TIMEOUT_MINUTES: Orphan timeout (default: 30)

    lazydocs: ignore
    """

    def __init__(self):
        """Initialize SQLite adapter.

        Loads configuration from environment variables, initializes database
        schema, and sets up connection pool.

        Raises:
            KeyError: If required configuration is missing
            ApplicationException: If schema initialization fails
        """
        # Load configuration
        self.db_path = required_env("RC_WORKITEM_DB_PATH")
        self.files_dir = Path(
            os.getenv("RC_WORKITEM_FILES_DIR", "devdata/work_item_files")
        )
        self.queue_name = os.getenv("RC_WORKITEM_QUEUE_NAME", "default")
        self.orphan_timeout_minutes = int(
            os.getenv("RC_WORKITEM_ORPHAN_TIMEOUT_MINUTES", "30")
        )

        # Create directories
        self.files_dir.mkdir(parents=True, exist_ok=True)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        # Initialize connection pool
        self._pool = ThreadLocalConnectionPool(
            factory=self._create_connection,
            cleanup=lambda conn: conn.close(),
        )

        # Initialize database schema
        self._init_database()

        LOGGER.info(
            "SQLiteAdapter initialized: db=%s, queue=%s, files_dir=%s",
            self.db_path,
            self.queue_name,
            self.files_dir,
        )

    def _create_connection(self) -> sqlite3.Connection:
        """Create a new SQLite connection with optimized settings.

        Returns:
            sqlite3.Connection: Configured connection with WAL mode
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row

        # Configure WAL mode and optimizations
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=5000")

        return conn

    def _init_database(self):
        """Initialize database schema with migrations.

        Creates schema_version table if needed and applies all pending migrations.

        Raises:
            ApplicationException: If schema version is incompatible or migration fails
        """
        with self._pool.acquire() as conn:
            # Create version table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()

            # Detect current version
            cursor = conn.execute("SELECT MAX(version) FROM schema_version")
            result = cursor.fetchone()
            current_version = result[0] if result and result[0] is not None else 0

            # Check for version mismatch
            if current_version > SCHEMA_VERSION:
                raise ApplicationException(
                    f"Database schema version ({current_version}) is newer than "
                    f"adapter supports ({SCHEMA_VERSION}). Please upgrade adapter."
                )

            # Apply migrations
            migrations = {
                1: self._migrate_to_v1,
                2: self._migrate_to_v2,
                3: self._migrate_to_v3,
                4: self._migrate_to_v4,
            }

            for version in range(current_version + 1, SCHEMA_VERSION + 1):
                LOGGER.info("Applying migration to version %d", version)
                self._apply_migration(conn, version, migrations[version])

            LOGGER.info("Database schema initialized (version %d)", SCHEMA_VERSION)

    def _apply_migration(
        self, conn: sqlite3.Connection, target_version: int, migration_func
    ):
        """Apply a schema migration within a transaction.

        Args:
            conn: Database connection
            target_version: Version number being migrated to
            migration_func: Function that performs migration

        Raises:
            ApplicationException: If migration fails
        """
        try:
            migration_func(conn)
            conn.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, CURRENT_TIMESTAMP)",
                (target_version,),
            )
            conn.commit()
            LOGGER.info("Successfully migrated to version %d", target_version)
        except Exception as e:
            conn.rollback()
            LOGGER.error("Migration to version %d failed: %s", target_version, e)
            raise ApplicationException(
                f"Migration to version {target_version} failed: {e}"
            )

    def _migrate_to_v1(self, conn: sqlite3.Connection):
        """Migration v1: Create initial schema.

        Creates work_items table with:
        - id: Primary key (UUID)
        - queue_name: Queue identifier
        - parent_id: Parent work item ID (for outputs)
        - payload: JSON data (stored as TEXT)
        - state: Processing state (PENDING/RESERVED/COMPLETED/FAILED)
        - created_at: Creation timestamp
        """
        conn.execute(
            f"""
            CREATE TABLE work_items (
                id TEXT PRIMARY KEY,
                queue_name TEXT NOT NULL,
                parent_id TEXT,
                payload TEXT,
                state TEXT DEFAULT '{ProcessingState.PENDING.value}' CHECK(state IN ({_STATE_VALUES_FOR_CHECK})),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES work_items(id)
            )
        """
        )

        conn.execute(
            """
            CREATE INDEX idx_queue_state ON work_items(queue_name, state, created_at)
        """
        )

        conn.execute(
            """
            CREATE INDEX idx_parent ON work_items(parent_id)
        """
        )

        conn.execute(
            """
            CREATE TABLE work_item_files (
                work_item_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (work_item_id, filename),
                FOREIGN KEY (work_item_id) REFERENCES work_items(id) ON DELETE CASCADE
            )
        """
        )

        LOGGER.info("Created initial schema (v1)")

    def _migrate_to_v2(self, conn: sqlite3.Connection):
        """Migration v2: Add exception tracking fields.

        Adds fields to record exceptions when work items fail:
        - exception_type: Exception class name
        - exception_code: Error code
        - exception_message: Error description
        """
        conn.execute("ALTER TABLE work_items ADD COLUMN exception_type TEXT")
        conn.execute("ALTER TABLE work_items ADD COLUMN exception_code TEXT")
        conn.execute("ALTER TABLE work_items ADD COLUMN exception_message TEXT")

        LOGGER.info("Added exception tracking fields (v2)")

    def _migrate_to_v3(self, conn: sqlite3.Connection):
        """Migration v3: Add timestamp fields for orphan recovery.

        Adds timestamp fields to track work item lifecycle:
        - reserved_at: When work item was reserved
        - released_at: When work item was released (completed/failed)

        These enable orphaned work item detection and recovery.
        """
        conn.execute("ALTER TABLE work_items ADD COLUMN reserved_at TIMESTAMP")
        conn.execute("ALTER TABLE work_items ADD COLUMN released_at TIMESTAMP")

        # Add partial index for orphan recovery queries
        conn.execute(
            f"""
            CREATE INDEX idx_orphan_check
            ON work_items(state, reserved_at)
            WHERE state='{ProcessingState.RESERVED.value}'
        """
        )

        LOGGER.info("Added timestamp fields and orphan index (v3)")

    def _migrate_to_v4(self, conn: sqlite3.Connection):
        """Migration v4: Update state constraint (historical migration).

        This migration was needed in the original implementation to change
        from 'DONE' to 'COMPLETED', but since we're starting fresh with
        State.DONE.value already being 'COMPLETED', this is a no-op.

        Retained for forward compatibility and future-proofing, ensuring that
        schema versioning remains consistent if older deployments or future migrations
        require this version step.
        """
        LOGGER.info(
            "Migration v4 (no-op: retained for forward compatibility; schema already uses COMPLETED)"
        )

    @with_retry(
        max_attempts=3,
        backoff_factor=0.1,
        exceptions=(sqlite3.OperationalError, DatabaseTemporarilyUnavailable),
    )
    def reserve_input(self) -> str:
        """Reserve next pending work item from queue.

        Atomically reserves the oldest PENDING work item using UPDATE...RETURNING.
        Updates state to RESERVED and sets reserved_at timestamp.

        Returns:
            str: Work item ID (UUID)

        Raises:
            EmptyQueue: If no pending work items available
            DatabaseTemporarilyUnavailable: If database is temporarily locked
        """
        with self._pool.acquire() as conn:
            try:
                LOGGER.debug(
                    "Reserving next input work item from queue: %s", self.queue_name
                )

                # Atomic reservation with RETURNING clause
                cursor = conn.execute(
                    """
                    UPDATE work_items
                    SET state = ?,
                        reserved_at = CURRENT_TIMESTAMP
                    WHERE id = (
                        SELECT id FROM work_items
                        WHERE queue_name = ? AND state = ?
                        ORDER BY created_at ASC
                        LIMIT 1
                    )
                    RETURNING id
                """,
                    (
                        ProcessingState.RESERVED.value,
                        self.queue_name,
                        ProcessingState.PENDING.value,
                    ),
                )

                result = cursor.fetchone()
                conn.commit()

                if not result:
                    raise EmptyQueue(
                        f"No pending work items in queue: {self.queue_name}"
                    )

                item_id = result[0]
                LOGGER.info("Reserved input work item: %s", item_id)
                return item_id

            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    LOGGER.warning("Database locked, retrying: %s", e)
                    raise DatabaseTemporarilyUnavailable(f"Database locked: {e}")
                raise

    def release_input(
        self,
        item_id: str,
        state: State,
        exception: Optional[dict] = None,
    ):
        """Release work item with terminal state.

        Updates work item state to COMPLETED or FAILED and records exception details if failed.

        Args:
            item_id: Work item ID
            state: Terminal state (State.DONE or State.FAILED)
            exception: Exception details dict with keys: type, code, message

        Raises:
            ValueError: If state is not terminal or exception details missing for FAILED state
        """
        if state not in (State.DONE, State.FAILED):
            raise ValueError(f"Release state must be DONE or FAILED, got {state}")

        # Extract exception details
        exception_type = None
        exception_code = None
        exception_message = None

        if exception:
            exception_type = exception.get("type")
            exception_code = exception.get("code")
            exception_message = exception.get("message")

        if state == State.FAILED and not exception_message:
            raise ValueError("exception['message'] required when state=FAILED")

        with self._pool.acquire() as conn:
            conn.execute(
                """
                UPDATE work_items
                SET state = ?,
                    released_at = CURRENT_TIMESTAMP,
                    exception_type = ?,
                    exception_code = ?,
                    exception_message = ?
                WHERE id = ?
            """,
                (
                    state.value,
                    exception_type,
                    exception_code,
                    exception_message,
                    item_id,
                ),
            )
            conn.commit()

        log_func = LOGGER.error if state == State.FAILED else LOGGER.info
        log_func(
            "Released work item %s with state %s (exception: %s)",
            item_id,
            state.value,
            exception_message if exception else None,
        )

    def create_output(
        self,
        parent_id: Optional[str],
        payload: Optional[JSONType] = None,
    ) -> str:
        """Create new output work item.

        Creates a work item in PENDING state in a separate output queue.
        This prevents outputs from being immediately re-queued as inputs.

        Output Queue Strategy:
            - Input queue: {queue_name} (e.g., "qa_forms")
            - Output queue: {queue_name}_output (e.g., "qa_forms_output")
            - Outputs are NOT consumed by reserve_input()

        Args:
            parent_id: Parent work item ID (None for root items)
            payload: JSON payload data (default: empty dict)

        Returns:
            str: New work item ID (UUID)
        """
        item_id = str(uuid.uuid4())
        payload_json = json.dumps(payload if payload is not None else {})
        output_queue = f"{self.queue_name}_output"

        LOGGER.debug(
            "Creating output work item for parent %s in queue %s",
            parent_id or "None",
            output_queue,
        )

        with self._pool.acquire() as conn:
            conn.execute(
                """
                INSERT INTO work_items (id, queue_name, parent_id, payload, state, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (
                    item_id,
                    output_queue,
                    parent_id,
                    payload_json,
                    ProcessingState.PENDING.value,
                ),
            )
            conn.commit()

        LOGGER.info("Created output work item: %s", item_id)
        return item_id

    def seed_input(
        self,
        payload: Optional[JSONType] = None,
        parent_id: str = "",
        files: Optional[list[tuple[str, bytes]]] = None,
    ) -> str:
        """Developer helper to create work item directly in input queue.

        This method is used by seeding scripts and tests to populate the queue
        with test data. Unlike create_output(), this creates items in the INPUT
        queue that can be consumed by reserve_input().

        Args:
            payload: JSON payload data
            parent_id: Parent work item ID (optional)
            files: List of (filename, content) tuples (optional)

        Returns:
            str: New work item ID
        """
        item_id = str(uuid.uuid4())
        payload_json = json.dumps(payload if payload is not None else {})

        LOGGER.debug(
            "Seeding input work item in queue %s with parent %s",
            self.queue_name,
            parent_id or "None",
        )

        with self._pool.acquire() as conn:
            conn.execute(
                """
                INSERT INTO work_items (id, queue_name, parent_id, payload, state, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
                (
                    item_id,
                    self.queue_name,  # Use input queue, not output
                    parent_id or None,
                    payload_json,
                    ProcessingState.PENDING.value,
                ),
            )
            conn.commit()

        # Add files if provided
        if files:
            for name, content in files:
                self.add_file(item_id, name, content)

        LOGGER.info("Seeded input work item: %s", item_id)
        return item_id

    def load_payload(self, item_id: str) -> dict:
        """Load JSON payload from work item.

        Args:
            item_id: Work item ID

        Returns:
            dict: JSON payload data

        Raises:
            ValueError: If work item not found
        """
        with self._pool.acquire() as conn:
            cursor = conn.execute(
                "SELECT payload FROM work_items WHERE id = ?", (item_id,)
            )
            result = cursor.fetchone()

            if not result:
                raise ValueError(f"Work item not found: {item_id}")

            payload = json.loads(result[0] or "{}")
            LOGGER.debug("Loaded payload for work item: %s", item_id)
            return payload

    def save_payload(self, item_id: str, payload: JSONType):
        """Save JSON payload to work item.

        Args:
            item_id: Work item ID
            payload: JSON payload data

        Raises:
            ValueError: If work item not found
        """
        payload_json = json.dumps(payload)

        with self._pool.acquire() as conn:
            cursor = conn.execute(
                "UPDATE work_items SET payload = ? WHERE id = ?",
                (payload_json, item_id),
            )

            if cursor.rowcount == 0:
                raise ValueError(f"Work item not found: {item_id}")

            conn.commit()
            LOGGER.debug("Saved payload for work item: %s", item_id)

    def list_files(self, item_id: str) -> list[str]:
        """List file attachments for work item.

        Args:
            item_id: Work item ID

        Returns:
            list[str]: List of filenames
        """
        with self._pool.acquire() as conn:
            cursor = conn.execute(
                "SELECT filename FROM work_item_files WHERE work_item_id = ? ORDER BY filename",
                (item_id,),
            )
            files = [row[0] for row in cursor.fetchall()]
            LOGGER.debug("Listed %d files for work item: %s", len(files), item_id)
            return files

    def get_file(self, item_id: str, name: str) -> bytes:
        """Retrieve file content from filesystem.

        Args:
            item_id: Work item ID
            name: Filename

        Returns:
            bytes: File content

        Raises:
            ValueError: If file not found or missing from filesystem
        """
        with self._pool.acquire() as conn:
            cursor = conn.execute(
                "SELECT filepath FROM work_item_files WHERE work_item_id = ? AND filename = ?",
                (item_id, name),
            )
            result = cursor.fetchone()

            if not result:
                raise FileNotFoundError(
                    f"File not found: {name} (work item: {item_id})"
                )

            filepath = Path(result[0])

            if not filepath.exists():
                raise ValueError(f"File missing from filesystem: {filepath}")

            content = filepath.read_bytes()
            LOGGER.debug("Retrieved file: %s (%d bytes)", name, len(content))
            return content

    def add_file(self, item_id: str, name: str, content: bytes):
        """Attach file to work item.

        Stores file on filesystem and creates database reference.

        Args:
            item_id: Work item ID
            name: Filename
            content: File content

        Raises:
            ValueError: If file already exists
        """
        # Create directory structure {files_dir}/{work_item_id}/{filename}
        item_dir = self.files_dir / item_id
        item_dir.mkdir(parents=True, exist_ok=True)
        filepath = item_dir / name

        LOGGER.debug(
            "Adding file '%s' to work item %s (%d bytes)", name, item_id, len(content)
        )

        if filepath.exists():
            raise FileExistsError(f"File already exists: {name} (work item: {item_id})")

        # Write file to filesystem
        filepath.write_bytes(content)

        # Create database record
        with self._pool.acquire() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO work_item_files (work_item_id, filename, filepath)
                    VALUES (?, ?, ?)
                """,
                    (item_id, name, str(filepath)),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # Cleanup file if database insert fails
                filepath.unlink(missing_ok=True)
                raise FileExistsError(
                    f"File already exists: {name} (work item: {item_id})"
                )

    def remove_file(self, item_id: str, name: str):
        """Remove file attachment.

        Deletes file from filesystem and removes database reference.

        Args:
            item_id: Work item ID
            name: Filename

        Raises:
            ValueError: If file not found
        """
        with self._pool.acquire() as conn:
            # Get filepath from database
            cursor = conn.execute(
                "SELECT filepath FROM work_item_files WHERE work_item_id = ? AND filename = ?",
                (item_id, name),
            )
            result = cursor.fetchone()

            if not result:
                raise FileNotFoundError(
                    f"File not found: {name} (work item: {item_id})"
                )

            filepath = Path(result[0])

            # Delete from database
            conn.execute(
                "DELETE FROM work_item_files WHERE work_item_id = ? AND filename = ?",
                (item_id, name),
            )
            conn.commit()

            # Delete from filesystem
            filepath.unlink(missing_ok=True)
            LOGGER.debug("Removed file: %s", name)

    def recover_orphaned_work_items(self) -> list[str]:
        """Recover orphaned work items beyond timeout.

        Resets RESERVED work items to PENDING if they've been reserved longer
        than the configured timeout threshold.

        Returns:
            list[str]: List of recovered work item IDs
        """
        with self._pool.acquire() as conn:
            modifier = f"+{self.orphan_timeout_minutes} minutes"
            cursor = conn.execute(
                """
                    UPDATE work_items
                    SET state = ?,
                        reserved_at = NULL
                    WHERE state = ?
                    AND datetime(reserved_at, ?) < datetime('now')
                    RETURNING id
                """,
                (
                    ProcessingState.PENDING.value,
                    ProcessingState.RESERVED.value,
                    modifier,
                ),
            )

            recovered_ids = [row[0] for row in cursor.fetchall()]
            conn.commit()

            if recovered_ids:
                LOGGER.warning(
                    "Recovered %d orphaned work items (timeout: %d min): %s",
                    len(recovered_ids),
                    self.orphan_timeout_minutes,
                    recovered_ids,
                )

            return recovered_ids
