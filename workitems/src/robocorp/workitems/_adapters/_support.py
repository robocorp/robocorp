"""Support utilities for custom work item adapters.

This module provides shared utilities used by SQLite, Redis, and DocumentDB
adapters, including connection pooling, retry logic, and migration helpers.
"""

import functools
import logging
import threading
import time
from contextlib import contextmanager
from typing import Any, Callable, Generic, Optional, TypeVar

from .._exceptions import ApplicationException

LOGGER = logging.getLogger(__name__)

T = TypeVar("T")


class ThreadLocalConnectionPool(Generic[T]):
    """Thread-local connection pool for database connections.

    Maintains one connection per thread, automatically creating and cleaning
    up connections as needed. This pattern is used by SQLite and Redis adapters
    to avoid sharing connections across threads.

    Example:
        pool = ThreadLocalConnectionPool(factory=create_connection)

        with pool.acquire() as conn:
            conn.execute("SELECT * FROM items")
    """

    def __init__(
        self, factory: Callable[[], T], cleanup: Optional[Callable[[T], None]] = None
    ):
        """Initialize the connection pool.

        Args:
            factory: Callable that creates a new connection
            cleanup: Optional callable that cleans up a connection before disposal
        """
        self._factory = factory
        self._cleanup = cleanup
        self._local = threading.local()
        self._lock = threading.Lock()

    @contextmanager
    def acquire(self):
        """Acquire a connection from the pool.

        Yields the thread-local connection, creating it if necessary.
        The connection is automatically returned to the pool after use.
        """
        if not hasattr(self._local, "connection"):
            with self._lock:
                # Double-check inside lock
                if not hasattr(self._local, "connection"):
                    LOGGER.debug(
                        "Creating new connection for thread %s",
                        threading.current_thread().name,
                    )
                    self._local.connection = self._factory()

        try:
            yield self._local.connection
        except Exception:
            # On error, close and remove the connection to get a fresh one next time
            self.close()
            raise

    def close(self):
        """Close and remove the thread-local connection."""
        if hasattr(self._local, "connection"):
            conn = self._local.connection
            if self._cleanup:
                try:
                    self._cleanup(conn)
                except Exception as e:
                    LOGGER.warning("Error cleaning up connection: %s", e)
            delattr(self._local, "connection")
            LOGGER.debug(
                "Closed connection for thread %s", threading.current_thread().name
            )


def with_retry(
    max_attempts: int = 3,
    backoff_factor: float = 1.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """Decorator that retries a function on failure with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including initial call)
        backoff_factor: Base delay between retries in seconds
        exceptions: Tuple of exception types to catch and retry

    Example:
        @with_retry(max_attempts=3, backoff_factor=0.5)
        def query_database(conn):
            return conn.execute("SELECT * FROM items")
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        delay = backoff_factor * (2**attempt)
                        LOGGER.warning(
                            "Attempt %d/%d failed: %s. Retrying in %.2fs...",
                            attempt + 1,
                            max_attempts,
                            e,
                            delay,
                        )
                        time.sleep(delay)
                    else:
                        LOGGER.error(
                            "All %d attempts failed. Last error: %s",
                            max_attempts,
                            e,
                        )

            # All attempts exhausted, raise the last exception
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def get_schema_version(conn: Any, adapter_type: str) -> int:
    """Get the current schema version from the database.

    Args:
        conn: Database connection (SQLite, Redis, or MongoDB client)
        adapter_type: Type of adapter ('sqlite', 'redis', 'docdb')

    Returns:
        Current schema version number

    Raises:
        ApplicationException: If schema version cannot be determined
    """
    try:
        if adapter_type == "sqlite":
            cursor = conn.execute("SELECT version FROM schema_version LIMIT 1")
            row = cursor.fetchone()
            return row[0] if row else 0
        elif adapter_type == "redis":
            version = conn.get("schema:version")
            return int(version) if version else 0
        elif adapter_type == "docdb":
            result = conn.metadata.find_one({"_id": "schema_version"})
            return result["version"] if result else 0
        else:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
    except Exception as e:
        raise ApplicationException(
            f"Failed to get schema version for {adapter_type}: {e}"
        )


def apply_migration(
    conn: Any,
    adapter_type: str,
    from_version: int,
    to_version: int,
    migration_func: Callable[[Any], None],
) -> None:
    """Apply a database migration.

    Args:
        conn: Database connection
        adapter_type: Type of adapter ('sqlite', 'redis', 'docdb')
        from_version: Current schema version
        to_version: Target schema version
        migration_func: Function that performs the migration

    Raises:
        ApplicationException: If migration fails
    """
    LOGGER.info(
        "Applying %s migration from version %d to %d",
        adapter_type,
        from_version,
        to_version,
    )

    try:
        migration_func(conn)

        # Update schema version
        if adapter_type == "sqlite":
            conn.execute(
                "INSERT OR REPLACE INTO schema_version (id, version) VALUES (1, ?)",
                (to_version,),
            )
            conn.commit()
        elif adapter_type == "redis":
            conn.set("schema:version", to_version)
        elif adapter_type == "docdb":
            conn.metadata.update_one(
                {"_id": "schema_version"},
                {"$set": {"version": to_version}},
                upsert=True,
            )

        LOGGER.info("Migration to version %d completed successfully", to_version)
    except Exception as e:
        LOGGER.error("Migration failed: %s", e)
        raise ApplicationException(f"Migration to version {to_version} failed: {e}")


def ensure_schema_version(
    conn: Any,
    adapter_type: str,
    current_version: int,
    required_version: int,
) -> None:
    """Ensure the schema version is compatible with the adapter.

    Args:
        conn: Database connection
        adapter_type: Type of adapter
        current_version: Current schema version
        required_version: Required schema version

    Raises:
        ApplicationException: If schema version is incompatible
    """
    if current_version > required_version:
        raise ApplicationException(
            f"{adapter_type} schema version {current_version} is newer than "
            f"supported version {required_version}. Please upgrade the adapter."
        )
