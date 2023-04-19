from robo_log import verify_log_messages_from_log_html


def test_log_with_iterators(tmpdir, ui_regenerate):
    from robo_log_tests._resources import check_iterators
    from imp import reload
    from robo_log_tests.fixtures import basic_log_setup

    with basic_log_setup(tmpdir) as setup_info:
        check_iterators = reload(check_iterators)
        check_iterators.main()

    log_target = setup_info.log_target
    assert log_target.exists()
    verify_log_messages_from_log_html(
        log_target,
        [],
    )
    setup_info.open_log_target()
