from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def resources_dir():
    resources = Path(__file__).parent / "resources"
    assert resources.exists()
    return resources


@pytest.fixture(autouse=True)
def set_check_truststore_false(monkeypatch):
    monkeypatch.setenv("RC_USE_TRUSTSTORE", "False")
