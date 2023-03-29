import tempfile
from pathlib import Path

import pytest

from robo_cli import rcc


@pytest.fixture
def tempdir():
    with tempfile.TemporaryDirectory() as tempdir:
        yield tempdir


def test_blank(tempdir):
    tempdir_path = Path(tempdir)
    path = rcc.new_project(tempdir_path / "blank", "blank")
    assert (path / ".gitignore").exists()
    assert (path / "pyproject.toml").exists()
    assert (path / "tasks.py").exists()


def test_browser(tempdir):
    tempdir_path = Path(tempdir)
    path = rcc.new_project(tempdir_path / "browser", "browser")
    assert (path / ".gitignore").exists()
    assert (path / "pyproject.toml").exists()
    assert (path / "tasks.py").exists()
