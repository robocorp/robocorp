import json
import logging
import sys
from concurrent.futures import Future, TimeoutError
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Iterator

import pytest

from robocorp.action_server._actions_process_pool import (
    ActionsProcessPool,
    ProcessHandle,
)
from robocorp.action_server._robo_utils.run_in_thread import run_in_thread


@pytest.fixture
def actions_process_pool(tmpdir):
    from robocorp.action_server._models import Action, ActionPackage
    from robocorp.action_server._settings import Settings

    datadir = Path(tmpdir / "datadir")
    artifacts_dir = datadir / "artifacts"
    settings = Settings(datadir=datadir, artifacts_dir=artifacts_dir, verbose=True)
    settings.reuse_processes = True
    settings.min_processes = 2
    settings.max_processes = 3

    action_package_id_to_action_package = {}
    actions = []

    action_package_dir = Path(tmpdir / "action_package")
    action_package_dir.mkdir(parents=True, exist_ok=True)
    action_file = action_package_dir / "action.py"
    action_file.write_text(
        """
from robocorp.actions import action

@action
def greet(name: str, title="Mr.") -> str:
    return f"Hello {title} {name}."
"""
    )

    env_json = json.dumps({"PYTHON_EXE": sys.executable})

    action_package = ActionPackage(
        id="action_package1",
        name="action_package",
        directory=str(action_package_dir),
        conda_hash="",
        env_json=env_json,
    )

    action = Action(
        id="action1",
        action_package_id=action_package.id,
        name="greet",
        docs="",
        file=str(action_file),
        lineno=0,
        input_schema="",
        output_schema="",
    )

    action_package_id_to_action_package[action_package.id] = action_package
    actions.append(action)

    ret = ActionsProcessPool(settings, action_package_id_to_action_package, actions)

    from logging import StreamHandler

    stream_handler = StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="[%Y-%m-%d %H:%M:%S]"
    )
    stream_handler.setFormatter(formatter)
    logger = logging.root
    old_level = logger.level
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    try:
        yield ret
    finally:
        ret.dispose()
        logger.setLevel(old_level)
        logger.removeHandler(stream_handler)


@dataclass
class _RunInfo:
    future: Future[int]
    input_json: Path
    result_json: Path
    output_file: Path
    process_handle: ProcessHandle


class _DummyRequest:
    def __init__(self, headers=None, cookies=None):
        self.headers = headers or {}
        self.cookies = cookies or {}


@contextmanager
def _create_run(
    tmpdir, actions_process_pool: ActionsProcessPool, action, i
) -> Iterator[_RunInfo]:
    """
    Returns a future which provides the returncode. Note: the `with` statement
    that uses this method should not return before `future.result()` is given.
    """
    p = Path(tmpdir)
    robot_artifacts = p / f"artifacts_{i}"
    robot_artifacts.mkdir(parents=True, exist_ok=True)
    input_json = robot_artifacts / "input.json"
    output_file = robot_artifacts / "output.txt"
    result_json = robot_artifacts / "result.json"
    request = _DummyRequest()
    input_json.write_text(json.dumps({"name": "John"}))

    with actions_process_pool.obtain_process_for_action(action) as process_handle:
        fut: Future[int] = run_in_thread(
            partial(
                process_handle.run_action,
                action,
                input_json,
                robot_artifacts,
                output_file,
                result_json,
                request,
                actions_process_pool._reuse_processes,
            )
        )
        yield _RunInfo(
            future=fut,
            input_json=input_json,
            result_json=result_json,
            output_file=output_file,
            process_handle=process_handle,
        )


def test_actions_process_pool_run(actions_process_pool: ActionsProcessPool, tmpdir):
    actions = actions_process_pool.actions
    assert len(actions) == 1
    action = next(iter(actions))

    for i in range(3):
        # Creates one action at a time here as we get the result and then move
        # on to the next.
        with _create_run(tmpdir, actions_process_pool, action, i) as run_info:
            assert run_info.future.result() == 0
            assert run_info.output_file.exists()
            assert run_info.result_json.exists()


def test_actions_process_pool_process_crash(
    actions_process_pool: ActionsProcessPool, tmpdir
):
    actions = actions_process_pool.actions
    assert len(actions) == 1
    action = next(iter(actions))

    # Creates one action at a time here as we get the result and then move
    # on to the next.
    with _create_run(tmpdir, actions_process_pool, action, 1) as run_info1:
        assert actions_process_pool.get_running_processes_count() == 1

        with _create_run(tmpdir, actions_process_pool, action, 2) as run_info2:
            assert actions_process_pool.get_running_processes_count() == 2

            with _create_run(tmpdir, actions_process_pool, action, 3) as run_info3:
                assert actions_process_pool.get_running_processes_count() == 3

                assert run_info1.future.result() == 0
                assert run_info2.future.result() == 0
                assert run_info3.future.result() == 0

                # Kill while process is checked-out.
                run_info3.process_handle.kill()

            assert actions_process_pool.get_running_processes_count() == 2
            # Usually it'd be 1 idle, but as it was killed it's not added.
            assert actions_process_pool.get_idle_processes_count() == 0

        assert actions_process_pool.get_running_processes_count() == 1
        assert actions_process_pool.get_idle_processes_count() == 1

        # Kill idle process
        run_info2.process_handle.kill()
        with _create_run(tmpdir, actions_process_pool, action, 4) as run_info4:
            assert run_info2.process_handle != run_info4.process_handle
            assert run_info4.future.result() == 0
            assert actions_process_pool.get_running_processes_count() == 2
            assert actions_process_pool.get_idle_processes_count() == 0


def test_actions_process_pool_max_concurrent(
    actions_process_pool: ActionsProcessPool, tmpdir
) -> None:
    actions = actions_process_pool.actions
    assert len(actions) == 1
    action = next(iter(actions))

    with _create_run(tmpdir, actions_process_pool, action, 1) as run_info1:
        assert actions_process_pool.get_running_processes_count() == 1

        with _create_run(tmpdir, actions_process_pool, action, 2) as run_info2:
            assert actions_process_pool.get_running_processes_count() == 2

            with _create_run(tmpdir, actions_process_pool, action, 3) as run_info3:
                assert actions_process_pool.get_running_processes_count() == 3

                assert run_info1.future.result() == 0
                assert run_info2.future.result() == 0
                assert run_info3.future.result() == 0

                assert actions_process_pool.get_idle_processes_count() == 0

                def _create_run_in_ctx():
                    # This won't complete until one of the previous context
                    # managers actually return.
                    with _create_run(
                        tmpdir, actions_process_pool, action, 4
                    ) as run_info4:
                        return run_info4.future.result()

                fut = run_in_thread(_create_run_in_ctx)
                with pytest.raises(TimeoutError):
                    # This will not complete here
                    fut.result(2)

            # It should complete now that one of the previous processes exited.
            assert fut.result(10) == 0
            assert actions_process_pool.get_running_processes_count() == 2
            assert actions_process_pool.get_idle_processes_count() == 1

        assert actions_process_pool.get_running_processes_count() == 1
        assert actions_process_pool.get_idle_processes_count() == 2

    assert actions_process_pool.get_running_processes_count() == 0
    assert actions_process_pool.get_idle_processes_count() == 2


def test_actions_process_pool_basic(actions_process_pool: ActionsProcessPool):
    actions = actions_process_pool.actions
    assert len(actions) == 1
    action = next(iter(actions))

    assert actions_process_pool.get_idle_processes_count() == 2
    assert actions_process_pool.get_running_processes_count() == 0
    with actions_process_pool.obtain_process_for_action(action) as p1:
        assert p1 is not None

        assert actions_process_pool.get_idle_processes_count() == 1
        assert actions_process_pool.get_running_processes_count() == 1

        with actions_process_pool.obtain_process_for_action(action) as p2:
            assert p2 is not None

            assert actions_process_pool.get_idle_processes_count() == 0
            assert actions_process_pool.get_running_processes_count() == 2

            with actions_process_pool.obtain_process_for_action(action) as p3:
                assert p3 is not None

                assert actions_process_pool.get_idle_processes_count() == 0
                assert actions_process_pool.get_running_processes_count() == 3
