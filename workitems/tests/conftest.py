import os
import socket
import time

import pytest

pytest_plugins = [
    "devutils.fixtures",
    "workitems_tests.fixtures",
]


def pytest_configure(config):
    """Register custom markers to silence PytestUnknownMark warnings."""
    config.addinivalue_line(
        "markers",
        "integration: tests requiring external services such as Redis or MongoDB (SQLite tests do NOT use this marker)",
    )
    config.addinivalue_line(
        "markers",
        "redis: tests requiring a running Redis instance",
    )
    config.addinivalue_line(
        "markers",
        "docdb: tests requiring a MongoDB/DocumentDB instance",
    )


def _wait_for_port(host: str, port: int, timeout: float = 5.0) -> bool:
    """Wait for a port to become available within timeout."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            time.sleep(0.1)
    return False


@pytest.fixture(scope="session")
def redis_available() -> bool:
    """Check if Redis is available on localhost:6379."""
    return _wait_for_port("localhost", 6379, timeout=2.0)


@pytest.fixture(scope="session")
def mongo_available() -> bool:
    """Check if MongoDB is available on localhost:27017."""
    return _wait_for_port("localhost", 27017, timeout=2.0)


@pytest.fixture(autouse=True)
def skip_if_redis_unavailable(request, redis_available):
    """Skip tests marked with 'redis' if Redis is not available."""
    if request.node.get_closest_marker("redis") and not redis_available:
        pytest.skip("Redis not available (run: cd tests/compose && ./up.sh)")


@pytest.fixture(autouse=True)
def skip_if_mongo_unavailable(request, mongo_available):
    """Skip tests marked with 'docdb' if MongoDB is not available."""
    if request.node.get_closest_marker("docdb") and not mongo_available:
        pytest.skip("MongoDB not available (run: cd tests/compose && ./up.sh)")


@pytest.fixture(autouse=True)
def integration_test_env(request, monkeypatch):
    """Set default environment variables for integration tests."""
    if (
        request.node.get_closest_marker("integration")
        or request.node.get_closest_marker("redis")
        or request.node.get_closest_marker("docdb")
    ):
        # Set defaults if not already set
        if "RC_REDIS_URL" not in os.environ:
            monkeypatch.setenv("RC_REDIS_URL", "redis://localhost:6379/0")
        if "RC_MONGO_URL" not in os.environ:
            monkeypatch.setenv("RC_MONGO_URL", "mongodb://localhost:27017")
        if "RC_MONGO_DB" not in os.environ:
            monkeypatch.setenv("RC_MONGO_DB", "workitems_test")
        if "RC_MONGO_COLL_PREFIX" not in os.environ:
            monkeypatch.setenv("RC_MONGO_COLL_PREFIX", "queue_")
