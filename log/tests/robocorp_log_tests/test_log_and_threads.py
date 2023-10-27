import threading


def test_log_and_threads(tmpdir):
    from importlib import reload

    from robocorp_log_tests._resources import check
    from robocorp_log_tests.fixtures import AutoLogConfigForTest, basic_log_setup

    from robocorp import log
    from robocorp.log import verify_log_messages_from_log_html

    config = AutoLogConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        check = reload(check)

        def run_in_thread():
            # This won't be logged (in auto-logging we check that logging
            # from threads aren't logged).
            check.some_method()

            # This won't be logged either because it's not in the main thread.
            log.critical("critical in log")

            # This is a special case though because we want to be able to request
            # a process snapshot from any thread.
            log.process_snapshot()

        t = threading.Thread(target=run_in_thread)
        t.start()
        t.join()

    log_target = setup_info.log_target
    assert log_target.exists()

    verify_log_messages_from_log_html(
        log_target,
        [
            {
                "message_type": "SPS",  # Start process snapshot
            },
            # At least main thread + 1 secondary thread logged.
            {
                "message_type": "STD",  # Start thread dump.
            },
            {
                "message_type": "STD",
            },
        ],
        [{"message_type": "L", "level": "E"}],
    )
