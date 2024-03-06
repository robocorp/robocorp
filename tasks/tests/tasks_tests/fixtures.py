from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def resources_dir():
    resources = Path(__file__).parent / "resources"
    assert resources.exists()
    return resources


@pytest.fixture(autouse=True)
def disable_truststore_injection(monkeypatch):
    """Disables truststore SSL injection during testing, so we'd avoid
    unnecessary warnings given the missing dependency."""

    monkeypatch.setenv("_RC_TEST_USE_TRUSTSTORE", "False")
