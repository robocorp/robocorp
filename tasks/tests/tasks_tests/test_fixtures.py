from collections.abc import Iterable

import pytest

from robocorp.tasks import setup as tasks_setup
from robocorp.tasks import teardown as tasks_teardown
from robocorp.tasks._hooks import (
    after_all_tasks_run,
    after_task_run,
    before_all_tasks_run,
    before_task_run,
)


@pytest.fixture(autouse=True)
def clear_callbacks():
    before_task_run._callbacks = ()
    before_all_tasks_run._callbacks = ()
    after_task_run._callbacks = ()
    after_all_tasks_run._callbacks = ()


def test_setup_default():
    assert len(before_task_run) == 0
    assert len(before_all_tasks_run) == 0

    is_called = False

    @tasks_setup
    def fixture(task):
        assert task == "placeholder"
        nonlocal is_called
        is_called = True

    assert not is_called
    assert len(before_task_run) == 1
    assert len(before_all_tasks_run) == 0

    before_task_run("placeholder")
    assert is_called


def test_setup_all():
    assert len(before_task_run) == 0
    assert len(before_all_tasks_run) == 0

    is_called = False

    @tasks_setup(scope="session")
    def fixture(tasks):
        assert isinstance(tasks, Iterable)
        nonlocal is_called
        is_called = True

    assert not is_called
    assert len(before_task_run) == 0
    assert len(before_all_tasks_run) == 1

    before_all_tasks_run([])
    assert is_called


def test_setup_task():
    assert len(before_task_run) == 0
    assert len(before_all_tasks_run) == 0

    is_called = False

    @tasks_setup(scope="task")
    def fixture(task):
        assert task == "placeholder"
        nonlocal is_called
        is_called = True

    assert not is_called
    assert len(before_task_run) == 1
    assert len(before_all_tasks_run) == 0

    before_task_run("placeholder")
    assert is_called


def test_teardown_default():
    assert len(after_task_run) == 0
    assert len(after_all_tasks_run) == 0

    is_called = False

    @tasks_teardown
    def fixture(task):
        assert task == "placeholder"
        nonlocal is_called
        is_called = True

    assert not is_called
    assert len(after_task_run) == 1
    assert len(after_all_tasks_run) == 0

    after_task_run("placeholder")
    assert is_called


def test_teardown_all():
    assert len(after_task_run) == 0
    assert len(after_all_tasks_run) == 0

    is_called = False

    @tasks_teardown(scope="session")
    def fixture(tasks):
        assert isinstance(tasks, Iterable)
        nonlocal is_called
        is_called = True

    assert not is_called
    assert len(after_task_run) == 0
    assert len(after_all_tasks_run) == 1

    after_all_tasks_run([])
    assert is_called


def test_teardown_task():
    assert len(after_task_run) == 0
    assert len(after_all_tasks_run) == 0

    is_called = False

    @tasks_teardown(scope="task")
    def fixture(task):
        assert task == "placeholder"
        nonlocal is_called
        is_called = True

    assert not is_called
    assert len(after_task_run) == 1
    assert len(after_all_tasks_run) == 0

    after_task_run("placeholder")
    assert is_called


def test_raises():
    @tasks_setup
    def raises_setup(_):
        raise RuntimeError("Oopsie")

    @tasks_teardown
    def raises_teardown(_):
        raise RuntimeError("Oopsie #2")

    assert len(before_task_run) == 1
    assert len(after_task_run) == 1

    with pytest.raises(RuntimeError):
        before_task_run(None)

    after_task_run(None)


def test_setup_generator():
    assert len(before_task_run) == 0
    assert len(after_task_run) == 0

    is_called = False

    @tasks_setup
    def fixture_gen(task):
        assert task == "task"
        yield
        nonlocal is_called
        is_called = True

    assert not is_called
    assert len(before_task_run) == 1
    assert len(after_task_run) == 0

    before_task_run("task")

    assert not is_called
    assert len(before_task_run) == 1
    assert len(after_task_run) == 1

    after_task_run("task")

    assert is_called
    assert len(before_task_run) == 1
    assert len(after_task_run) == 0
