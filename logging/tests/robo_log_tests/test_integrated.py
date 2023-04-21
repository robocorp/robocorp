from robo_log import verify_log_messages_from_log_html


def test_log_with_iterators(tmpdir, ui_regenerate):
    from robo_log_tests._resources import check_iterators
    from imp import reload
    from robo_log_tests.fixtures import basic_log_setup
    from robo_log_tests.fixtures import ConfigForTest

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
                "message_type": "YR",
                "name": "iterate_entries_in_project",
                "libname": "robo_log_tests._resources.check_iterators",
            },
            {
                "message_type": "YS",
                "type": "int",
                "value": "2",
            },
            {
                "message_type": "SE",
                "name": "iterator_in_library",
                "libname": "robo_log_tests._resources.check_iterators_lib",
                "type": "UNTRACKED_GENERATOR",
            },
        ],
    )
    # for m in msgs:
    #     print(m)
    # setup_info.open_log_target()
