"""
This module should provide a basic example on the usage of the logging.
"""
import threading


def test_log_api(tmpdir) -> None:
    from robocorp import log
    from robocorp_log_tests._resources import check
    from imp import reload
    from robocorp.log import verify_log_messages_from_log_html
    from robocorp_log_tests.fixtures import basic_log_setup

    with basic_log_setup(tmpdir, max_file_size="30kb", max_files=1) as setup_info:
        check = reload(check)
        check.some_method()

        log.info("Some message")
        log.critical("Some e message")
        log.warn("Some w message")

        # Calls from thread won't appear in the auto-logging right now.
        t = threading.Thread(target=check.some_method, args=())
        t.start()
        t.join(10)

        t = threading.Thread(target=log.info, args=("SHOULD NOT APPEAR",))
        t.start()
        t.join(10)

    assert setup_info.log_target.exists()
    messages = verify_log_messages_from_log_html(
        setup_info.log_target,
        [
            dict(message_type="SE", name="some_method"),
            dict(message_type="SE", name="call_another_method"),
            dict(message_type="L", level="I", message="Some message"),
            dict(message_type="L", level="E", message="Some e message"),
            dict(message_type="L", level="W", message="Some w message"),
        ],
        [],
    )
    # Calls in thread not logged.
    assert str(messages).count("call_another_method") == 1
    assert str(messages).count("SHOULD NOT APPEAR") == 0


def test_log_api_without_with_statments(tmpdir) -> None:
    from robocorp import log
    from robocorp_log_tests._resources import check
    from imp import reload
    from pathlib import Path
    from robocorp.log import verify_log_messages_from_log_html

    log_target = Path(tmpdir.join("log.html"))
    ctx = log.setup_auto_logging()
    try:
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
    finally:
        ctx.__exit__(None, None, None)
