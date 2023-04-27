from robocorp.log import verify_log_messages_from_log_html


def test_log_with_yield_iterator(tmpdir, ui_regenerate):
    from robocorp_log_tests._resources import check_iterators
    from imp import reload
    from robocorp_log_tests.fixtures import basic_log_setup
    from robocorp_log_tests.fixtures import ConfigForTest
    from robocorp.log._decoder import MESSAGE_TYPE_YIELD_SUSPEND
    from robocorp.log._decoder import MESSAGE_TYPE_YIELD_RESUME

    config = ConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        check_iterators = reload(check_iterators)
        check_iterators.main()

    log_target = setup_info.log_target
    assert log_target.exists()
    msgs = verify_log_messages_from_log_html(
        log_target,
        [
            {
                "message_type": MESSAGE_TYPE_YIELD_RESUME,
                "name": "iterate_entries_in_project",
                "libname": "robocorp_log_tests._resources.check_iterators",
            },
            {
                "message_type": MESSAGE_TYPE_YIELD_SUSPEND,
                "type": "int",
                "value": "2",
            },
            {
                "message_type": "SE",
                "name": "iterator_in_library",
                "libname": "robocorp_log_tests._resources.check_iterators_lib",
                "type": "UNTRACKED_GENERATOR",
            },
        ],
    )
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_log_with_yield_iterator_augassign(tmpdir, ui_regenerate):
    from robocorp_log_tests._resources import check_iterators
    from imp import reload
    from robocorp_log_tests.fixtures import basic_log_setup
    from robocorp_log_tests.fixtures import ConfigForTest
    from robocorp.log._decoder import MESSAGE_TYPE_YIELD_SUSPEND
    from robocorp.log._decoder import MESSAGE_TYPE_YIELD_RESUME

    config = ConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        check_iterators = reload(check_iterators)
        check_iterators.main_yield_augassign()

    log_target = setup_info.log_target
    assert log_target.exists()
    msgs = verify_log_messages_from_log_html(
        log_target,
        [
            {
                "message_type": MESSAGE_TYPE_YIELD_SUSPEND,
                "name": "yield_augassign",
                "libname": "robocorp_log_tests._resources.check_iterators",
                "type": "str",
                "value": "'aug1'",
            },
            {
                "message_type": MESSAGE_TYPE_YIELD_RESUME,
                "name": "yield_augassign",
                "libname": "robocorp_log_tests._resources.check_iterators",
            },
            {
                "message_type": MESSAGE_TYPE_YIELD_SUSPEND,
                "name": "yield_augassign",
                "libname": "robocorp_log_tests._resources.check_iterators",
                "type": "str",
                "value": "' aug2'",
            },
            {
                "message_type": MESSAGE_TYPE_YIELD_RESUME,
                "name": "yield_augassign",
                "libname": "robocorp_log_tests._resources.check_iterators",
            },
            {
                "message_type": MESSAGE_TYPE_YIELD_SUSPEND,
                "name": "yield_augassign",
                "libname": "robocorp_log_tests._resources.check_iterators",
                "type": "str",
                "value": "' aug3'",
            },
            {
                "message_type": MESSAGE_TYPE_YIELD_RESUME,
                "name": "yield_augassign",
                "libname": "robocorp_log_tests._resources.check_iterators",
            },
            {
                "message_type": "EE",
                "type": "GENERATOR",
                "status": "PASS",
            },
        ],
    )
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()


def test_log_with_yield_from_iterator(tmpdir, ui_regenerate):
    from robocorp_log_tests._resources import check_iterators
    from imp import reload
    from robocorp_log_tests.fixtures import basic_log_setup
    from robocorp_log_tests.fixtures import ConfigForTest
    from robocorp.log._decoder import MESSAGE_TYPE_YIELD_FROM_RESUME
    from robocorp.log._decoder import MESSAGE_TYPE_YIELD_FROM_SUSPEND

    config = ConfigForTest()
    with basic_log_setup(tmpdir, config=config) as setup_info:
        check_iterators = reload(check_iterators)
        check_iterators.main_yield_from()

    log_target = setup_info.log_target
    assert log_target.exists()
    msgs = verify_log_messages_from_log_html(
        log_target,
        [
            {
                "message_type": MESSAGE_TYPE_YIELD_FROM_SUSPEND,
                "name": "yield_from",
                "libname": "robocorp_log_tests._resources.check_iterators",
            },
            {
                "message_type": MESSAGE_TYPE_YIELD_FROM_RESUME,
                "name": "yield_from",
                "libname": "robocorp_log_tests._resources.check_iterators",
            },
        ],
    )
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()
