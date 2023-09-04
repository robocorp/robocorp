import io
from pathlib import Path
from typing import Dict

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
    import os

    matrix_name = os.environ.get("GITHUB_ACTIONS_MATRIX_NAME")
    if matrix_name:
        if "devmode" not in matrix_name:
            # i.e.: When testing with log in release mode we can't use
            # the hack to import the tests.
            pytest.skip(f"Disabled for matrix name: {matrix_name}")

    from robocorp.log import verify_log_messages_from_log_html
    from robocorp_log_tests.fixtures import pretty_format_logs_from_log_html

    result = robocorp_tasks_run(["run", "simple.py"], returncode=0, cwd=str(datadir))

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


def test_core_log_integration_empty_pyproject(datadir) -> None:
    pyproject: Path = datadir / "pyproject.toml"
    pyproject.write_text(
        """
[tool.robocorp.log]
default_library_filter_kind = "exclude"
"""
    )
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


def test_core_log_integration_lines(datadir, str_regression) -> None:
    from robocorp_log_tests.fixtures import pretty_format_logs_from_log_html

    result = robocorp_tasks_run(
        ["run", "main_check_lines.py"], returncode=0, cwd=str(datadir)
    )

    decoded = result.stderr.decode("utf-8", "replace")
    decoded = result.stdout.decode("utf-8", "replace")
    assert "Robocorp Log (html)" in decoded

    log_target = datadir / "output" / "log.html"
    assert log_target.exists()

    str_regression.check(
        pretty_format_logs_from_log_html(
            log_target, show_log_messages=True, show_lines=True
        )
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


@pytest.fixture
def server_socket():
    import socket

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (
        "localhost",
        0,
    )
    server_socket.bind(server_address)
    server_socket.listen(1)

    class _ServerSocketFacade:
        def __init__(self):
            self.sockname = server_socket.getsockname()
            self.received_data = []

        @property
        def port(self) -> int:
            return self.sockname[1]

    facade = _ServerSocketFacade()

    def server_on_thread():
        client_socket, _client_address = server_socket.accept()

        while True:
            # Receive data from the client
            data = client_socket.recv(1024)  # Receive up to 1024 bytes of data
            if not data:
                break
            facade.received_data.append(data.decode("utf-8"))

    import threading

    t = threading.Thread(target=server_on_thread)
    t.start()

    yield facade


def test_receive_at_socket(datadir, server_socket) -> None:
    from robocorp.log import verify_log_messages_from_stream

    pyproject: Path = datadir / "pyproject.toml"
    pyproject.write_text("")

    port = server_socket.port

    additional_env: Dict[str, str] = {"ROBOCORP_TASKS_LOG_LISTENER_PORT": str(port)}
    result = robocorp_tasks_run(
        ["run", "--console-color=plain", "simple.py"],
        returncode=0,
        cwd=str(datadir),
        additional_env=additional_env,
    )

    data = "".join(server_socket.received_data)

    s = io.StringIO(data)
    msgs = verify_log_messages_from_stream(
        s,
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


def test_output_on_change_cwd(datadir) -> None:
    pyproject: Path = datadir / "pyproject.toml"
    pyproject.write_text("")

    result = robocorp_tasks_run(
        ["run", "--console-color=plain", "change_cwd.py"],
        returncode=0,
        cwd=str(datadir),
    )

    decoded = result.stderr.decode("utf-8", "replace")
    assert not decoded.strip(), f"Found stderr: {decoded}"
    decoded = result.stdout.decode("utf-8", "replace")
    assert "Robocorp Log (html)" in decoded

    assert (datadir / "output" / "log.html").exists()


def test_use_robot_artifacts_env_var_for_output(datadir, tmpdir) -> None:
    pyproject: Path = datadir / "pyproject.toml"
    pyproject.write_text("")

    result = robocorp_tasks_run(
        ["run", "--console-color=plain", "simple.py"],
        returncode=0,
        cwd=str(datadir),
        additional_env={"ROBOT_ARTIFACTS": str(tmpdir / "output_check")},
    )

    decoded = result.stderr.decode("utf-8", "replace")
    assert not decoded.strip(), f"Found stderr: {decoded}"
    decoded = result.stdout.decode("utf-8", "replace")
    assert "Robocorp Log (html)" in decoded

    assert (tmpdir / "output_check" / "log.html").exists()
