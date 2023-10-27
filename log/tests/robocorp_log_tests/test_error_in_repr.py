from robocorp.log import verify_log_messages_from_log_html


def test_error_in_repr(tmpdir):
    from importlib import reload

    from robocorp_log_tests._resources import check_repr_error
    from robocorp_log_tests.fixtures import basic_log_setup

    with basic_log_setup(tmpdir) as setup_info:
        check_repr_error = reload(check_repr_error)
        check_repr_error.main()

    log_target = setup_info.log_target
    assert log_target.exists()
    verify_log_messages_from_log_html(
        log_target,
        [
            {
                "message_type": "EA",
                "name": "arg",
                "type": "ErrorInRepr",
                "value": "<error getting repr: Cannot do repr!>",
            }
        ],
    )
    # setup_info.open_log_target()
