def test_errors(log_setup, tmpdir):
    from importlib import reload

    from robocorp_log_tests._resources import check_traceback

    from robocorp import log
    from robocorp.log import verify_log_messages_from_stream
    from robocorp.log.protocols import Status

    stream = log_setup["stream"]

    # i.e.: make sure that it's loaded with the ast rewriting.
    check_traceback = reload(check_traceback)

    log.start_run("My Run")
    log.start_task("task", "modname", str(tmpdir), 0)

    try:
        check_traceback.main()
    except RuntimeError as e:
        log.end_task("task", "modname", Status.ERROR, str(e))
        log.end_run("My Run", Status.ERROR)
    else:
        raise AssertionError("Expected error and it was not raised.")

    stream.seek(0)
    verify_log_messages_from_stream(
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
