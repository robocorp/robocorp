def test_rotate_logs(tmpdir):
    import robocorp_logging
    from robocorp_logging_tests._resources import check
    from imp import reload
    from pathlib import Path
    from robocorp_logging import iter_decoded_log_format

    log_target = Path(tmpdir.join("log.html"))

    with robocorp_logging.setup_auto_logging():
        check = reload(check)

        with robocorp_logging.add_log_output(
            tmpdir, max_file_size="10kb", max_files=2, log_html=log_target
        ):
            robocorp_logging.log_start_suite("Root Suite", "root", str(tmpdir))
            robocorp_logging.log_start_task("my_task", "task_id", 0, [])

            check.recurse_some_method()

            robocorp_logging.log_end_task("my_task", "task_id", "PASS", "Ok")
            robocorp_logging.log_end_suite("Root Suite", "root", "PASS")

        assert log_target.exists()

    files = tuple(Path(tmpdir).glob("*.robolog"))
    assert len(files) == 2, f"Found: {files}"

    name_to_file = dict((f.name, f) for f in files)
    assert set(name_to_file.keys()) == {"output_10.robolog", "output_11.robolog"}
    output_at_step = name_to_file["output_10.robolog"]

    # Check that replay suite/test/keyword are properly sent on rotate.
    expect_types = {"RS", "RT", "RE"}
    found_ids_at_step = []
    with output_at_step.open("r") as stream:
        for msg in iter_decoded_log_format(stream):
            if msg["message_type"] == "ID":
                found_ids_at_step.append(msg)
            expect_types.discard(msg["message_type"])
            if not expect_types:
                break
        else:
            raise AssertionError(f"Some expected messages not found: {expect_types}")
    assert found_ids_at_step[0]["part"] == 10
