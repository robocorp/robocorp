import tempfile
from pathlib import Path

import pytest

from robo_cli import templates


@pytest.fixture
def tempdir():
    with tempfile.TemporaryDirectory() as tempdir:
        yield Path(tempdir)


def test_blank(tempdir):
    path = tempdir / "blank"
    templates.copy_template(path, "blank")
    assert (path / ".gitignore").exists()
    assert (path / "pyproject.toml").exists()
    assert (path / "tasks.py").exists()


def test_browser(tempdir):
    path = tempdir / "browser"
    templates.copy_template(path, "browser")
    assert (path / ".gitignore").exists()
    assert (path / "pyproject.toml").exists()
    assert (path / "tasks.py").exists()
