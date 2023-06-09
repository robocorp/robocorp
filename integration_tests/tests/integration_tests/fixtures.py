from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def integration_resources_dir():
    f = Path(__file__)

    resources_dir = f.parent / ".." / ".." / "resources"
    resources_dir = resources_dir.absolute()
    assert resources_dir.exists()
    return resources_dir
