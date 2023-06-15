def test_impl_recovery_matches_suite() -> None:
    from robocorp.log._robo_output_impl import _Config, _RoboOutputImpl

    config = _Config("uuid")
    config.output_dir = None
    config.max_file_size_in_bytes = 9999999999
    config.max_files = 1
    config.log_html = None
    config.min_messages_per_file = 10

    impl = _RoboOutputImpl(config)
    impl.start_run("suite1", 0)
    impl.start_task("test1", "modname", __file__, 0, "", 0)
    assert len(impl._stack_handler._queue) == 2

    # Unsynchronized end suite (clear until we reach it).
    impl.end_run("suite1", "PASS", 0)

    assert len(impl._stack_handler._queue) == 0


def test_impl_recovery_matches_task() -> None:
    from robocorp.log._robo_output_impl import _Config, _RoboOutputImpl

    config = _Config("uuid")
    config.output_dir = None
    config.max_file_size_in_bytes = 9999999999
    config.max_files = 1
    config.log_html = None
    config.min_messages_per_file = 10

    impl = _RoboOutputImpl(config)
    impl.start_run("suite1", 0)
    impl.start_task("test1", "modname", "source", 0, "", 0)
    impl.start_element(
        "My Keyword", "libname", "METHOD", "doc", "source", 0, 0, [], False
    )
    assert len(impl._stack_handler._queue) == 3

    # Unsynchronized end task (clear until we reach it).
    impl.end_task("test1", "modname", "PASS", "", 0)
    assert len(impl._stack_handler._queue) == 1
    impl.end_run("suite1", "PASS", 0)
    assert len(impl._stack_handler._queue) == 0


def test_impl_recovery_does_not_match_test() -> None:
    from robocorp.log._robo_output_impl import _Config, _RoboOutputImpl

    config = _Config("uuid")
    config.output_dir = None
    config.max_file_size_in_bytes = 9999999999
    config.max_files = 1
    config.log_html = None
    config.min_messages_per_file = 10

    impl = _RoboOutputImpl(config)
    impl.start_run("suite1", 0)
    impl.start_task("test1", "modname", "source", 0, "", 0)
    impl.start_element(
        "My Keyword", "libname", "METHOD", "doc", "source", 0, 0, [], False
    )
    assert len(impl._stack_handler._queue) == 3

    # Unsynchronized end task (clear all methods).
    impl.end_task("no-match", "modname", "PASS", "", 0)
    assert len(impl._stack_handler._queue) == 1
    impl.end_run("suite1", "PASS", 0)
    assert len(impl._stack_handler._queue) == 0


def test_impl_recovery_do_nothing() -> None:
    from robocorp.log._robo_output_impl import _Config, _RoboOutputImpl

    config = _Config("uuid")
    config.output_dir = None
    config.max_file_size_in_bytes = 9999999999
    config.max_files = 1
    config.log_html = None
    config.min_messages_per_file = 10

    impl = _RoboOutputImpl(config)
    impl.end_run("suite1", "PASS", 0)
    assert len(impl._stack_handler._queue) == 0
