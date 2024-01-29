import json
import os

import pytest
from devutils.fixtures import robocorp_tasks_run


@pytest.fixture(autouse=True)
def _fix_pythonpath():
    import sys

    if "tasks" in sys.modules:
        # We have tasks.py and tasks/__init__.py in different tests, so, proactively
        # remove it.
        del sys.modules["tasks"]

    from robocorp.tasks._collect_tasks import clear_previously_collected_tasks

    clear_previously_collected_tasks()

    yield

    if "tasks" in sys.modules:
        # We have tasks.py and tasks/__init__.py in different tests, so, proactively
        # remove it.
        del sys.modules["tasks"]


def test_colect_tasks(datadir):
    from robocorp.tasks._collect_tasks import collect_tasks

    tasks = tuple(collect_tasks(datadir, "main"))
    assert len(tasks) == 1

    tasks = tuple(collect_tasks(datadir, ""))
    assert len(tasks) == 4
    assert {t.name for t in tasks} == {"main", "sub", "main_errors", "task_with_args"}
    name_to_task = dict((t.name, f"{t.module_name}.{t.name}") for t in tasks)
    assert name_to_task == {
        "main": "tasks.main",
        "sub": "sub.sub_task.sub",
        "main_errors": "tasks.main_errors",
        "task_with_args": "tasks.task_with_args",
    }

    tasks = tuple(collect_tasks(datadir, "not_there"))
    assert len(tasks) == 0


def test_colect_tasks_from_package(datadir):
    from robocorp.tasks._collect_tasks import collect_tasks

    tasks = tuple(collect_tasks(datadir / "in_init"))
    assert len(tasks) == 1


def test_collect_tasks_integrated_error(tmpdir):
    result = robocorp_tasks_run(
        ["run", "dir_not_there", "-t=main"], returncode=1, cwd=str(tmpdir)
    )

    decoded = result.stdout.decode("utf-8", "replace")
    if "dir_not_there does not exist" not in decoded:
        raise AssertionError(f"Unexpected stdout: {decoded}")


def test_collect_tasks_integrated(datadir):
    from robocorp.log import verify_log_messages_from_log_html

    result = robocorp_tasks_run(
        ["run", str(datadir), "-t", "main"], returncode=0, cwd=datadir
    )

    assert not result.stderr, f"Error with command line: {result.args}: {result.stderr.decode('utf-8', 'replace')}"
    assert "In some method" in result.stdout.decode("utf-8")

    # That's the default.
    log_html = datadir / "output" / "log.html"
    assert log_html.exists(), "log.html not generated."
    verify_log_messages_from_log_html(
        log_html,
        [
            dict(message_type="SE", name="some_method"),
            dict(message_type="ST"),
            dict(message_type="ET"),
            dict(message_type="SR"),
            dict(message_type="ER"),
        ],
    )


def test_list_tasks_api(datadir, tmpdir, data_regression):
    def check(result):
        output = result.stdout.decode("utf-8")
        loaded = json.loads(output)
        assert len(loaded) == 4
        for entry in loaded:
            entry["file"] = os.path.basename(entry["file"])
        data_regression.check(loaded)

    # List with the dir as a target
    result = robocorp_tasks_run(["list", str(datadir)], returncode=0, cwd=str(tmpdir))
    check(result)

    # List without the dir as a target (must have the same output).
    result = robocorp_tasks_run(["list"], returncode=0, cwd=datadir)
    check(result)


def test_provide_output_in_stdout(datadir, tmpdir):
    from robocorp.log import verify_log_messages_from_decoded_str

    result = robocorp_tasks_run(
        ["run", "-t=main", str(datadir), "--output", str(tmpdir)],
        returncode=0,
        additional_env={"RC_LOG_OUTPUT_STDOUT": "1"},
    )

    verify_log_messages_from_decoded_str(
        result.stdout.decode("utf-8"),
        [
            dict(message_type="SE", name="some_method"),
            dict(message_type="ST"),
            dict(message_type="ET"),
            dict(message_type="SR"),
            dict(message_type="ER"),
        ],
    )


def test_error_in_stdout(datadir, tmpdir):
    from robocorp.log import verify_log_messages_from_decoded_str

    result = robocorp_tasks_run(
        ["run", "-t=main_errors", str(datadir), "--output", str(tmpdir)],
        returncode=1,
        additional_env={"RC_LOG_OUTPUT_STDOUT": "1"},
    )

    msgs = verify_log_messages_from_decoded_str(
        result.stdout.decode("utf-8"),
        [
            dict(message_type="SE", name="main_errors"),
            dict(message_type="ST"),
            dict(message_type="ET"),
            dict(message_type="SR"),
            dict(message_type="ER"),
            dict(message_type="STB"),
        ],
    )
    count = 0
    for msg in msgs:
        if msg["message_type"] == "STB":
            count += 1

    assert count == 1, "Only one Start Traceback message expected."


def test_collect_duplicated_tasks(datadir, tmpdir):
    result = robocorp_tasks_run(
        ["run", str(datadir / "dupe" / "dupe.py")],
        returncode=1,
        additional_env={"RC_LOG_OUTPUT_STDOUT": "1"},
    )
    assert "a task with the name 'main' was already found" in str(
        result.stdout.decode("utf-8")
    )
