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


def run(cmdline, returncode, cwd=None):
    import os

    cp = os.environ.copy()
    cp["PYTHONPATH"] = os.pathsep.join([x for x in sys.path if x])
    args = [sys.executable, "-m", "robo"] + cmdline
    result = subprocess.run(args, capture_output=True, env=cp, cwd=cwd)
    if result.returncode != returncode:
        env_str = "\n".join(str(x) for x in sorted(cp.items()))

        raise AssertionError(
            f"""Expected returncode: {returncode}. Found: {result.returncode}.
=== stdout:
{result.stdout.decode('utf-8')}

=== stderr:
{result.stderr.decode('utf-8')}

=== Env:
{env_str}

=== Args:
{args}

"""
        )
    return result


def test_collect_tasks_integrated_error(tmpdir):
    result = run(["run", "dir_not_there", "-t=main"], returncode=1, cwd=str(tmpdir))

    decoded = result.stderr.decode("utf-8", "replace")
    if "dir_not_there does not exist" not in decoded:
        raise AssertionError(f"Unexpected stderr: {decoded}")


def verify_log_messages(log_html, expected):
    from robocorp_logging import iter_decoded_log_format_from_log_html

    log_messages = tuple(iter_decoded_log_format_from_log_html(log_html))
    for log_msg in log_messages:
        for expected_dct in expected:
            for key, val in expected_dct.items():
                if log_msg.get(key) != val:
                    break
            else:
                expected.remove(expected_dct)

    if expected:
        new_line = "\n"
        raise AssertionError(
            f"Did not find {expected}.\nFound:\n{new_line.join(str(x) for x in log_messages)}"
        )


def test_collect_tasks_integrated(datadir):
    result = run(["run", str(datadir), "-t", "main"], returncode=0, cwd=datadir)

    assert (
        not result.stderr
    ), f"Error with command line: {result.args}: {result.stderr.decode('utf-8', 'replace')}"
    assert "In some method" in result.stdout.decode("utf-8")

    # That's the default.
    log_html = datadir / "output" / "log.html"
    assert log_html.exists(), "log.html not generated."
    verify_log_messages(
        log_html,
        [
            dict(message_type="SK", name="some_method"),
            dict(message_type="ST"),
            dict(message_type="ET"),
            dict(message_type="SS"),
            dict(message_type="ES"),
        ],
    )
