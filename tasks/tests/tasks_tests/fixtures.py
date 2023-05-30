from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def resources_dir():
    resources = Path(__file__).parent / "resources"
    assert resources.exists()
    return resources
