from tasks_tests.fixtures import robo_run
from pathlib import Path


def test_core_log_integration_error_in_import(datadir):
    from robocorp.log import verify_log_messages_from_log_html

    result = robo_run(
        ["run", "main_with_error_in_import.py"], returncode=1, cwd=str(datadir)
    )

    decoded = result.stderr.decode("utf-8", "replace")
    assert (
        "ModuleNotFoundError: No module named 'module_that_does_not_exist'" in decoded
    )
    decoded = result.stdout.decode("utf-8", "replace")

    log_target = datadir / "output" / "log.html"
    assert log_target.exists()

    msgs = verify_log_messages_from_log_html(
        log_target,
        [
            {
                "message_type": "STB",
                "message": "ModuleNotFoundError: No module named 'module_that_does_not_exist'",
            },
            # Note: the setup is a task which doesn't have a suite!
            {
                "message_type": "ST",
                "name": "Collect tasks",
                "libname": "setup",
                "lineno": 0,
            },
            {
                "message_type": "ET",
                "status": "ERROR",
                "message": "No module named 'module_that_does_not_exist'",
            },
        ],
    )

    if False:  # Manually debugging
        for m in msgs:
            print(m)

        import webbrowser

        webbrowser.open(log_target.as_uri())


def test_core_log_integration_config_log(datadir):
    from robocorp.log import verify_log_messages_from_log_html

    result = robo_run(["run", "simple.py"], returncode=0, cwd=str(datadir))

    decoded = result.stderr.decode("utf-8", "replace")
    assert not decoded.strip()
    decoded = result.stdout.decode("utf-8", "replace")
    assert "Robocorp Log (html)" in decoded

    log_target = datadir / "output" / "log.html"
    assert log_target.exists()

    msgs = verify_log_messages_from_log_html(
        log_target,
        [{"message_type": "SE", "name": "ndiff"}],
    )

    assert "SequenceMatcher.__init__" not in str(msgs)

    if False:  # Manually debugging
        for m in msgs:
            print(m)

        import webbrowser

        webbrowser.open(log_target.as_uri())


def test_core_log_integration_empty_pyproject(datadir) -> None:
    pyproject: Path = datadir / "pyproject.toml"
    pyproject.write_text("")
    from robocorp.log import verify_log_messages_from_log_html

    result = robo_run(["run", "simple.py"], returncode=0, cwd=str(datadir))

    decoded = result.stderr.decode("utf-8", "replace")
    assert not decoded.strip()
    decoded = result.stdout.decode("utf-8", "replace")
    assert "Robocorp Log (html)" in decoded

    log_target = datadir / "output" / "log.html"
    assert log_target.exists()

    verify_log_messages_from_log_html(
        log_target,
        [{"message_type": "SE", "name": "check_difflib_log"}],
        [{"message_type": "SE", "name": "ndiff"}],
    )
