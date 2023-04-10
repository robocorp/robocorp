def test_impl_recovery_matches_suite():
    from robocorp_logging._impl import _RobotOutputImpl, _Config

    config = _Config("uuid")
    config.output_dir = None
    config.max_file_size_in_bytes = 9999999999
    config.max_files = 1
    config.log_html = None
    impl = _RobotOutputImpl(config)
    impl.start_suite("My Suite", "suite1", "", 0)
    impl.start_task("My Test", "test1", 0, 0, [])
    assert len(impl._stack_handler._queue) == 2

    # Unsynchronized end suite (clear until we reach it).
    impl.end_suite("suite1", "PASS", 0)

    assert len(impl._stack_handler._queue) == 0


def test_impl_recovery_matches_task():
    from robocorp_logging._impl import _RobotOutputImpl, _Config

    config = _Config("uuid")
    config.output_dir = None
    config.max_file_size_in_bytes = 9999999999
    config.max_files = 1
    config.log_html = None
    impl = _RobotOutputImpl(config)
    impl.start_suite("My Suite", "suite1", "", 0)
    impl.start_task("My Test", "test1", 0, 0, [])
    impl.start_element(
        "My Keyword", "libname", "KEYWORD", "doc", "source", 0, 0, [], []
    )
    assert len(impl._stack_handler._queue) == 3

    # Unsynchronized end task (clear until we reach it).
    impl.end_task("test1", "PASS", "", 0)
    assert len(impl._stack_handler._queue) == 1
    impl.end_suite("suite1", "PASS", 0)
    assert len(impl._stack_handler._queue) == 0


def test_impl_recovery_does_not_match_test():
    from robocorp_logging._impl import _RobotOutputImpl, _Config

    config = _Config("uuid")
    config.output_dir = None
    config.max_file_size_in_bytes = 9999999999
    config.max_files = 1
    config.log_html = None
    impl = _RobotOutputImpl(config)
    impl.start_suite("My Suite", "suite1", "", 0)
    impl.start_task("My Test", "test1", 0, 0, [])
    impl.start_element(
        "My Keyword", "libname", "KEYWORD", "doc", "source", 0, 0, [], []
    )
    assert len(impl._stack_handler._queue) == 3

    # Unsynchronized end task (clear all methods).
    impl.end_task("no-match", "PASS", "", 0)
    assert len(impl._stack_handler._queue) == 1
    impl.end_suite("suite1", "PASS", 0)
    assert len(impl._stack_handler._queue) == 0


def test_impl_recovery_do_nothing():
    from robocorp_logging._impl import _RobotOutputImpl, _Config

    config = _Config("uuid")
    config.output_dir = None
    config.max_file_size_in_bytes = 9999999999
    config.max_files = 1
    config.log_html = None
    impl = _RobotOutputImpl(config)
    impl.end_suite("suite1", "PASS", 0)
    assert len(impl._stack_handler._queue) == 0
