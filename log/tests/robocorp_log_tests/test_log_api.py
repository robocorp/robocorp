"""
This module should provide a basic example on the usage of the logging.
"""
import contextlib
import threading


def test_log_api(tmpdir, str_regression) -> None:
    import io
    from importlib import reload

    from robocorp_log_tests._resources import check
    from robocorp_log_tests.fixtures import (
        basic_log_setup,
        pretty_format_logs_from_log_html,
    )

    from robocorp import log

    stdout = io.StringIO()
    stderr = io.StringIO()
    with basic_log_setup(tmpdir, max_file_size="30kb", max_files=1) as setup_info:
        with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(stdout):
            check = reload(check)
            check.some_method()

            log.info("Some message")
            log.critical("Some e message")
            log.warn("Some w message")
            log.debug("Some d message")

            with log.setup_log(log_level="warn"):
                log.debug("Hide d message")
                log.warn("Some w2 message")

                with log.setup_log(
                    output_log_level=log.FilterLogLevel.DEBUG, output_stream="stdout"
                ):
                    # This one will appear in the output but not as log message.
                    log.debug("msg-debug")

                    # This one will appear in both
                    log.critical("msg-critical")

            # Calls from thread won't appear in the auto-logging right now.
            t = threading.Thread(target=check.some_method, args=())
            t.start()
            t.join(10)

            t = threading.Thread(target=log.info, args=("SHOULD NOT APPEAR",))
            t.start()
            t.join(10)

    assert stderr.getvalue() == "Some e message\n"
    assert stdout.getvalue() == "msg-debug\nmsg-critical\n"

    assert setup_info.log_target.exists()
    str_regression.check(
        pretty_format_logs_from_log_html(
            setup_info.log_target, show_console_messages=True, show_log_messages=True
        )
    )


def test_log_api_without_with_statments(tmpdir) -> None:
    from importlib import reload
    from pathlib import Path

    from robocorp_log_tests._resources import check

    from robocorp import log
    from robocorp.log import verify_log_messages_from_log_html

    log_target = Path(tmpdir.join("log.html"))
    with log.setup_auto_logging():
        try:
            check = reload(check)

            log.add_log_output(
                tmpdir, max_file_size="30kb", max_files=1, log_html=log_target
            )

            log.start_run("Run name")
            log.start_task("my_task", "modname", __file__, 0)

            check.some_method()

            log.end_task("my_task", "modname", "PASS", "Ok")
            log.end_run("Run name", "PASS")

            assert not log_target.exists()
        finally:
            log.close_log_outputs()

        assert log_target.exists()
        verify_log_messages_from_log_html(log_target, [dict(message_type="SE")], [])
