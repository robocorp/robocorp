"""
This module should provide a basic example on the usage of the logging.
"""
import threading


def test_log_api(tmpdir) -> None:
    import robocorp_logging
    from robocorp_logging_tests._resources import check
    from imp import reload
    from pathlib import Path
    from robocorp_logging import iter_decoded_log_format_from_log_html
    from robocorp_logging_tests.fixtures import (
        verify_log_messages_from_messages_iterator,
    )

    log_target = Path(tmpdir.join("log.html"))

    with robocorp_logging.setup_auto_logging():
        check = reload(check)

        with robocorp_logging.add_log_output(
            tmpdir, max_file_size="30kb", max_files=1, log_html=log_target
        ):
            robocorp_logging.log_start_suite("Root Suite", "root", str(tmpdir))
            robocorp_logging.log_start_task("my_task", "task_id", 0, [])

            check.some_method()

            robocorp_logging.log_info("Some message")
            robocorp_logging.log_error("Some e message")
            robocorp_logging.log_warn("Some w message")

            # Calls from thread won't appear in the auto-logging right now.
            t = threading.Thread(target=check.some_method, args=())
            t.start()
            t.join(10)

            t = threading.Thread(
                target=robocorp_logging.log_info, args=("SHOULD NOT APPEAR",)
            )
            t.start()
            t.join(10)

            robocorp_logging.log_end_task("my_task", "task_id", "PASS", "Ok")
            robocorp_logging.log_end_suite("Root Suite", "root", "PASS")

        assert log_target.exists()
        messages = verify_log_messages_from_messages_iterator(
            iter_decoded_log_format_from_log_html(log_target),
            [
                dict(message_type="SE", name="some_method"),
                dict(message_type="SE", name="call_another_method"),
                dict(message_type="L", level="I", message="Some message"),
                dict(message_type="L", level="E", message="Some e message"),
                dict(message_type="L", level="W", message="Some w message"),
            ],
        )
        # Calls in thread not logged.
        assert str(messages).count("call_another_method") == 1
        assert str(messages).count("SHOULD NOT APPEAR") == 0


def test_log_api_without_with_statments(tmpdir) -> None:
    import robocorp_logging
    from robocorp_logging_tests._resources import check
    from imp import reload
    from pathlib import Path
    from robocorp_logging import iter_decoded_log_format_from_log_html
    from robocorp_logging_tests.fixtures import (
        verify_log_messages_from_messages_iterator,
    )

    log_target = Path(tmpdir.join("log.html"))
    ctx = robocorp_logging.setup_auto_logging()
    try:
        try:
            check = reload(check)

            robocorp_logging.add_log_output(
                tmpdir, max_file_size="30kb", max_files=1, log_html=log_target
            )

            robocorp_logging.log_start_suite("Root Suite", "root", str(tmpdir))
            robocorp_logging.log_start_task("my_task", "task_id", 0, [])

            check.some_method()

            robocorp_logging.log_end_task("my_task", "task_id", "PASS", "Ok")
            robocorp_logging.log_end_suite("Root Suite", "root", str(tmpdir))

            assert not log_target.exists()
        finally:
            robocorp_logging.close_log_outputs()

        assert log_target.exists()
        verify_log_messages_from_messages_iterator(
            iter_decoded_log_format_from_log_html(log_target), [dict(message_type="SE")]
        )
    finally:
        ctx.__exit__(None, None, None)
