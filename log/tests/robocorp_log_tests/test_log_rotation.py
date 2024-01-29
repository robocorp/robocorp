def test_rotate_logs(tmpdir, str_regression) -> None:
    from importlib import reload
    from pathlib import Path

    from robocorp_log_tests._resources import check
    from robocorp_log_tests.fixtures import pretty_format_logs_from_log_html  # noqa

    from robocorp import log as robolog
    from robocorp.log import iter_decoded_log_format_from_stream

    log_target = Path(tmpdir.join("log.html"))

    with robolog.setup_auto_logging():
        check = reload(check)

        with robolog.add_log_output(
            tmpdir,
            max_file_size="10kb",
            max_files=2,
            log_html=log_target,
            min_messages_per_file=10,
        ):
            robolog.start_run("Root Suite")
            robolog.start_task("my_task", "task_mod", __file__, 0)

            check.recurse_some_method()

            robolog.end_task("my_task", "task_mod", "PASS", "Ok")
            robolog.end_run("Root Suite", "PASS")

        assert log_target.exists()

    files = tuple(Path(tmpdir).glob("*.robolog"))
    assert len(files) == 2, f"Found: {files}"

    name_to_file = dict((f.name, f) for f in files)

    expected = 17
    assert set(name_to_file.keys()) == {
        f"output_{expected-1}.robolog",
        f"output_{expected}.robolog",
    }
    output_at_step = name_to_file[f"output_{expected}.robolog"]

    # Check that replay suite/test/keyword are properly sent on rotate.
    expect_types = {"RR", "RT", "RE"}
    found_ids_at_step = []
    with output_at_step.open("r") as stream:
        for msg in iter_decoded_log_format_from_stream(stream):
            if msg["message_type"] == "ID":
                found_ids_at_step.append(msg)
            expect_types.discard(msg["message_type"])
            if not expect_types:
                break
        else:
            raise AssertionError(f"Some expected messages not found: {expect_types}")
    assert found_ids_at_step[0]["part"] == expected

    # Depending on the times printed it may break a bit different.
    # str_regression.check(pretty_format_logs_from_log_html(log_target))
