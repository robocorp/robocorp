"""
This module should provide a basic example on the usage of the logging.
"""


def test_log_api(datadir, data_regression, tmpdir) -> None:
    import robocorp_logging
    from robocorp_logging_tests._resources import check
    from imp import reload
    from pathlib import Path
    from robocorp_logging import iter_decoded_log_format_from_log_html

    log_target = Path(tmpdir.join("log.html"))

    with robocorp_logging.setup_auto_logging():
        check = reload(check)

        with robocorp_logging.add_logging_output(
            tmpdir, max_file_size="30kb", max_files=1, log_html=log_target
        ):

            robocorp_logging.log_start_suite("Root Suite", "root", str(tmpdir))
            robocorp_logging.log_start_task("my_task", "task_id", 0, [])

            check.some_method()

            robocorp_logging.log_end_task("my_task", "task_id", "PASS", "Ok")
            robocorp_logging.log_end_suite("Root Suite", "root", str(tmpdir))

        assert log_target.exists()
        start_method_messages = []
        for v in iter_decoded_log_format_from_log_html(log_target):
            if v["message_type"] == "SK":
                start_method_messages.append(v)

        assert len(start_method_messages) > 1
