from pathlib import Path

import pytest
from devutils.fixtures import robocorp_tasks_run


def test_core_log_integration_error_in_import(datadir):
    from robocorp.log import verify_log_messages_from_log_html

    result = robocorp_tasks_run(
        ["run", "main_with_error_in_import.py"], returncode=1, cwd=str(datadir)
    )

    decoded = result.stderr.decode("utf-8", "replace")
    if (
        "ModuleNotFoundError: No module named 'module_that_does_not_exist'"
        not in decoded
    ):
        raise AssertionError(
            f"Expected: 'ModuleNotFoundError: No module named 'module_that_does_not_exist' to be in: {decoded}"
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


def test_core_log_integration_config_log(datadir, str_regression):
    import sys

    from robocorp import log

    f = Path(log.__file__)
    tests = f.parent.parent.parent.parent / "tests"
    assert tests.exists()
    # Hack to be able to use robocorp_log_tests.fixtures in the ci
    # without actually exporting it in pyproject.toml.
    sys.path.append(str(tests))
    try:
        from robocorp.log import verify_log_messages_from_log_html
        from robocorp_log_tests.fixtures import pretty_format_logs_from_log_html

        result = robocorp_tasks_run(
            ["run", "simple.py"], returncode=0, cwd=str(datadir)
        )

        decoded = result.stderr.decode("utf-8", "replace")
        assert not decoded.strip()
        decoded = result.stdout.decode("utf-8", "replace")
        assert "Robocorp Log (html)" in decoded

        log_target = datadir / "output" / "log.html"
        assert log_target.exists()

        str_regression.check(pretty_format_logs_from_log_html(log_target))
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
    finally:
        sys.path.remove(str(tests))


def test_core_log_integration_empty_pyproject(datadir) -> None:
    pyproject: Path = datadir / "pyproject.toml"
    pyproject.write_text("")
    from robocorp.log import verify_log_messages_from_log_html

    result = robocorp_tasks_run(["run", "simple.py"], returncode=0, cwd=str(datadir))

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


@pytest.mark.parametrize(
    "mode",
    [
        "plain",
        "ansi",
    ],
)
def test_core_log_integration_console_messages(datadir, str_regression, mode) -> None:
    pyproject: Path = datadir / "pyproject.toml"
    pyproject.write_text("")
    from robocorp.log import verify_log_messages_from_log_html

    result = robocorp_tasks_run(
        ["run", f"--console-colors={mode}", "simple.py"], returncode=0, cwd=str(datadir)
    )

    decoded = result.stderr.decode("utf-8", "replace")
    assert not decoded.strip()
    decoded = result.stdout.decode("utf-8", "replace")
    str_regression.check_until_header(decoded)

    log_target = datadir / "output" / "log.html"
    assert log_target.exists()

    msgs = verify_log_messages_from_log_html(
        log_target,
        [
            {
                "message_type": "C",
                "message": "\nCollecting tasks from: simple.py\n",
                "kind": "regular",
            },
            {
                "message_type": "C",
                "kind": "stdout",
                "message": "  aaaa  bbb- ccc+ eee  ddd",
            },
        ],
    )
    # for m in msgs:
    #     print(m)


@pytest.mark.parametrize("no_error_rc", [True, False])
def test_no_status_rc(datadir, no_error_rc) -> None:
    pyproject: Path = datadir / "pyproject.toml"
    pyproject.write_text("")
    from robocorp.log import verify_log_messages_from_log_html

    result = robocorp_tasks_run(
        ["run"]
        + (["--no-status-rc"] if no_error_rc else [])
        + ["--console-color=plain", "expected_error_in_task.py"],
        returncode=0 if no_error_rc else 1,
        cwd=str(datadir),
    )

    decoded = result.stderr.decode("utf-8", "replace")
    assert not decoded.strip()
    decoded = result.stdout.decode("utf-8", "replace")
    assert "Robocorp Log (html)" in decoded

    log_target = datadir / "output" / "log.html"
    assert log_target.exists()

    verify_log_messages_from_log_html(
        log_target,
        [{"message_type": "ER", "status": "ERROR"}],
    )
