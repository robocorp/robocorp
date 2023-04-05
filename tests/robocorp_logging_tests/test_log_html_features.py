import subprocess
import sys
import os

# Must be set to False when merging to master and
# python -m dev build-output-view
# must also be manually called afterwards.
FORCE_REGEN_DEV = False

# Must be set to false when merging to master.
OPEN_IN_BROWSER = False


def test_log_html_features(tmpdir) -> None:
    """
    This is a test which should generate an output for a log.html which
    showcases all the features available.
    """
    cwd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if FORCE_REGEN_DEV:
        subprocess.check_call(
            [sys.executable, "-m", "dev", "build-output-view", "dev"], cwd=cwd
        )
    else:
        subprocess.check_call(
            [sys.executable, "-m", "dev", "build-output-view"], cwd=cwd
        )

    import robocorp_logging
    from robocorp_logging_tests._resources import (
        check,
        check_sensitive_data,
        check_traceback,
    )
    from imp import reload
    from pathlib import Path
    from robocorp_logging import iter_decoded_log_format_from_log_html

    __tracebackhide__ = 1

    log_target = Path(tmpdir.join("log.html"))

    with robocorp_logging.setup_auto_logging():
        check = reload(check)
        check_sensitive_data = reload(check_sensitive_data)
        check_traceback = reload(check_traceback)

        with robocorp_logging.add_log_output(
            tmpdir, max_file_size="500kb", max_files=1, log_html=log_target
        ):
            robocorp_logging.log_start_suite("Root Suite", "root", str(tmpdir))
            robocorp_logging.log_start_task("my_task", "task_id", 0, [])

            for _i in range(20):
                check.some_method()
                robocorp_logging.log_error("Some log error")
                robocorp_logging.log_warn("Some log warn")
                robocorp_logging.log_info("Some log info")
                check_sensitive_data.run()
                try:
                    check_traceback.main()
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("Expected RuntimeError.")

            robocorp_logging.log_end_task(
                "my_task",
                "task_id",
                "ERROR",
                "Marking that it exited with error due to some reason...",
            )
            robocorp_logging.log_end_suite("Root Suite", "root", str(tmpdir))

        assert log_target.exists()
        if FORCE_REGEN_DEV:
            for v in iter_decoded_log_format_from_log_html(
                Path(os.path.join(os.path.dirname(log_target), "bundle.js"))
            ):
                print(v)
        else:
            for v in iter_decoded_log_format_from_log_html(log_target):
                print(v)

        if OPEN_IN_BROWSER:
            import webbrowser

            webbrowser.open(log_target.as_uri())
