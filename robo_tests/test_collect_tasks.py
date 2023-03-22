import subprocess
import sys


def test_colect_tasks(datadir):
    from robo._collect_tasks import collect_tasks

    tasks = tuple(collect_tasks(datadir, "main"))
    assert len(tasks) == 1

    tasks = tuple(collect_tasks(datadir, ""))
    assert len(tasks) == 2
    assert {t.name for t in tasks} == {"main", "sub"}
    name_to_task = dict((t.name, f"{t.package_name}.{t.name}") for t in tasks)
    assert name_to_task == {"main": "tasks.main", "sub": "sub.sub_task.sub"}

    tasks = tuple(collect_tasks(datadir, "not_there"))
    assert len(tasks) == 0


def run(cmdline):
    import os

    cp = os.environ.copy()
    cp["PYTHONPATH"] = os.pathsep.join([x for x in sys.path if x])
    return subprocess.run(
        [sys.executable, "-m", "robo"] + cmdline, capture_output=True, env=cp
    )


def test_collect_tasks_integrated_error():
    result = run(["run", "dir_not_there", "main"])

    assert "dir_not_there does not exist" in result.stderr.decode("utf-8", "replace")
    assert result.returncode == 1


def test_collect_tasks_integrated(datadir):
    from robocorp_logging import iter_decoded_log_format_from_log_html

    result = run(["run", str(datadir), "main"])

    assert (
        not result.stderr
    ), f"Error with command line: {result.args}: {result.stderr.decode('utf-8', 'replace')}"
    assert "In some method" in result.stdout.decode("utf-8")
    assert result.returncode == 0

    log_html = datadir / "output" / "log.html"
    assert log_html.exists(), "log.html not generated."
    log_messages = tuple(iter_decoded_log_format_from_log_html(log_html))
    for log_msg in log_messages:
        if log_msg["message_type"] == "SK" and log_msg["name"] == "some_method":
            break
    else:
        new_line = "\n"
        raise AssertionError(
            f"Did not find SK/some_method message. Found: {new_line.join(str(x) for x in log_messages)}"
        )
