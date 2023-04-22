"""
This module should provide a basic example on the usage of the logging.
"""
import threading


def test_log_api(tmpdir) -> None:
    from robocorp import robolog
    from robolog_tests._resources import check
    from imp import reload
    from robocorp.robolog import verify_log_messages_from_log_html
    from robolog_tests.fixtures import basic_log_setup

    with basic_log_setup(tmpdir, max_file_size="30kb", max_files=1) as setup_info:
        check = reload(check)
        check.some_method()

        robolog.info("Some message")
        robolog.critical("Some e message")
        robolog.warn("Some w message")

        # Calls from thread won't appear in the auto-logging right now.
        t = threading.Thread(target=check.some_method, args=())
        t.start()
        t.join(10)

        t = threading.Thread(target=robolog.info, args=("SHOULD NOT APPEAR",))
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
    from robocorp import robolog
    from robolog_tests._resources import check
    from imp import reload
    from pathlib import Path
    from robocorp.robolog import verify_log_messages_from_log_html

    log_target = Path(tmpdir.join("log.html"))
    ctx = robolog.setup_auto_logging()
    try:
        try:
            check = reload(check)

            robolog.add_log_output(
                tmpdir, max_file_size="30kb", max_files=1, log_html=log_target
            )

            robolog.start_run("Run name")
            robolog.start_task("my_task", "modname", __file__, 0, [])

            check.some_method()

            robolog.end_task("my_task", "modname", "PASS", "Ok")
            robolog.end_run("Run name", "PASS")

            assert not log_target.exists()
        finally:
            robolog.close_log_outputs()

        assert log_target.exists()
        verify_log_messages_from_log_html(log_target, [dict(message_type="SE")], [])
    finally:
        ctx.__exit__(None, None, None)
