import pytest


@pytest.fixture
def _fix_pythonpath(datadir):
    import sys

    p = str(datadir / "different_root")
    sys.path.append(p)
    if "tasks" in sys.modules:
        # We have tasks.py and tasks/__init__.py in different tests, so, proactively
        # remove it.
        del sys.modules["tasks"]
    yield

    sys.path.remove(p)
    if "tasks" in sys.modules:
        # We have tasks.py and tasks/__init__.py in different tests, so, proactively
        # remove it.
        del sys.modules["tasks"]


def test_colect_tasks_resolves_with_pythonpath(datadir, _fix_pythonpath):
    from robocorp.tasks._collect_tasks import collect_tasks
    from robocorp.tasks._customization._plugin_manager import PluginManager

    tasks = tuple(collect_tasks(PluginManager(), datadir / "different_root" / "tasks"))
    assert len(tasks) == 1, f"Found tasks: {tasks}"
