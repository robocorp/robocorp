def test_errors(log_setup, tmpdir):
    from robo_log_tests._resources import check_traceback
    from imp import reload
    import robo_log
    from robo_log import verify_log_messages_from_stream
    from robo_log.protocols import Status

    stream = log_setup["stream"]

    # i.e.: make sure that it's loaded with the ast rewriting.
    check_traceback = reload(check_traceback)

    robo_log.start_run("My Run")
    robo_log.start_task("task", "modname", str(tmpdir), 0, [])

    try:
        check_traceback.main()
    except RuntimeError as e:
        robo_log.end_task("task", "modname", Status.ERROR, str(e))
        robo_log.end_run("My Run", Status.ERROR)
    else:
        raise AssertionError("Expected error and it was not raised.")

    stream.seek(0)
    msgs = verify_log_messages_from_stream(
        stream,
        [
            dict(message_type="EE", status=Status.ERROR),
            dict(message_type="EE", status=Status.ERROR),
            dict(message_type="EE", status=Status.ERROR),
            dict(message_type="ET", status=Status.ERROR),
            dict(message_type="ER", status=Status.ERROR),
            dict(message_type="STB", message="RuntimeError: Fail here"),
            dict(
                message_type="TBE",
                method="sub_method",
                line_content='raise RuntimeError("Fail here")',
            ),
            dict(message_type="ETB"),
            {
                "message_type": "TBV",
                "name": "arg_name",
                "type": "tuple",
                "value": "('arg', 'name', 1)",
            },
        ],
    )
    assert stream.getvalue().count("STB") == 1
    # for m in msgs:
    #     print()
