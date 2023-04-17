"""
This module should provide a basic example on the usage of the logging.
"""
import threading


def test_log_api(tmpdir) -> None:
    import robo_log
    from robo_log_tests._resources import check
    from imp import reload
    from robo_log import verify_log_messages_from_log_html
    from robo_log_tests.fixtures import basic_log_setup

    with basic_log_setup(tmpdir, max_file_size="30kb", max_files=1) as setup_info:
        check = reload(check)
        check.some_method()

        robo_log.info("Some message")
        robo_log.critical("Some e message")
        robo_log.warn("Some w message")

        # Calls from thread won't appear in the auto-logging right now.
        t = threading.Thread(target=check.some_method, args=())
        t.start()
        t.join(10)

        t = threading.Thread(target=robo_log.info, args=("SHOULD NOT APPEAR",))
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
    )
    # Calls in thread not logged.
    assert str(messages).count("call_another_method") == 1
    assert str(messages).count("SHOULD NOT APPEAR") == 0


def test_log_api_without_with_statments(tmpdir) -> None:
    import robo_log
    from robo_log_tests._resources import check
    from imp import reload
    from pathlib import Path
    from robo_log import verify_log_messages_from_log_html

    log_target = Path(tmpdir.join("log.html"))
    ctx = robo_log.setup_auto_logging()
    try:
        try:
            check = reload(check)

            robo_log.add_log_output(
                tmpdir, max_file_size="30kb", max_files=1, log_html=log_target
            )

            robo_log.start_run("Run name")
            robo_log.start_task("my_task", "modname", __file__, 0, [])

            check.some_method()

            robo_log.end_task("my_task", "modname", "PASS", "Ok")
            robo_log.end_run("Run name", "PASS")

            assert not log_target.exists()
        finally:
            robo_log.close_log_outputs()

        assert log_target.exists()
        verify_log_messages_from_log_html(log_target, [dict(message_type="SE")])
    finally:
        ctx.__exit__(None, None, None)
