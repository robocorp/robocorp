import subprocess
import sys
import os
from typing import List, Any
from robo_log.protocols import LogHTMLStyle

# Must be set to False when merging to master and
# python -m dev build-output-view
# must also be manually called afterwards.
FORCE_REGEN: List[Any] = []

# Must be set to false when merging to master.
OPEN_IN_BROWSER = False

LOG_HTML_STYLE: LogHTMLStyle = "standalone"

if False:
    FORCE_REGEN.append("dev")
    OPEN_IN_BROWSER = True

    # LOG_HTML_STYLE = "vscode"
    LOG_HTML_STYLE = "standalone"

    if LOG_HTML_STYLE == "vscode":
        FORCE_REGEN.append(1)
    else:
        FORCE_REGEN.append(2)


def test_log_html_features(tmpdir) -> None:
    """
    This is a test which should generate an output for a log.html which
    showcases all the features available.
    """
    from robo_log_tests.fixtures import (
        verify_log_messages_from_messages_iterator,
    )

    cwd = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if FORCE_REGEN:
        cmd = [sys.executable, "-m", "dev", "build-output-view"]
        if "dev" in FORCE_REGEN:
            cmd.append("--dev")

        versions: List[int] = []
        for setting in FORCE_REGEN:
            if isinstance(setting, int):
                versions.append(setting)

        if versions:
            cmd.append(f"--version={','.join(str(x) for x in versions)}")
            subprocess.check_call(cmd, cwd=cwd)

    import robo_log
    from robo_log_tests._resources import (
        check,
        check_sensitive_data,
        check_traceback,
    )
    from imp import reload
    from pathlib import Path
    from robo_log import iter_decoded_log_format_from_log_html

    __tracebackhide__ = 1

    log_target = Path(tmpdir.join("log.html"))

    with robo_log.setup_auto_logging():
        check = reload(check)
        check_sensitive_data = reload(check_sensitive_data)
        check_traceback = reload(check_traceback)

        with robo_log.add_log_output(
            tmpdir,
            max_file_size="500kb",
            max_files=1,
            log_html=log_target,
            log_html_style=LOG_HTML_STYLE,
        ):
            robo_log.log_start_suite(
                "Test Log HTML Features", "root", str(tmpdir)
            )
            robo_log.log_start_task("my_task", "task_id", 0, [])

            for _i in range(2):
                check.some_method()
                robo_log.log_error("Some log error")
                robo_log.log_warn("Some log warn")
                robo_log.log_info("Some log info")
                check_sensitive_data.run()
                try:
                    check_traceback.main()
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("Expected RuntimeError.")
                try:
                    check_traceback.call_exc_with_context()
                except ValueError:
                    pass
                else:
                    raise AssertionError("Expected RuntimeError.")

            robo_log.log_end_task(
                "my_task",
                "task_id",
                "ERROR",
                "Marking that it exited with error due to some reason...",
            )
            robo_log.log_end_suite("Root Suite", "root", str(tmpdir))

        assert log_target.exists()
        if "dev" in FORCE_REGEN:
            messages_iterator = iter_decoded_log_format_from_log_html(
                Path(os.path.join(os.path.dirname(log_target), "bundle.js"))
            )
        else:
            messages_iterator = iter_decoded_log_format_from_log_html(log_target)

        msgs = verify_log_messages_from_messages_iterator(
            messages_iterator,
            [
                {
                    "message_type": "L",
                    "level": "E",
                    "message": "Some log error",
                },
                {
                    "message_type": "L",
                    "level": "W",
                    "message": "Some log warn",
                },
                {
                    "message_type": "L",
                    "level": "I",
                    "message": "Some log info",
                },
                {
                    "message_type": "STB",
                    "message": "RuntimeError: initial exc",
                },
                {
                    "message_type": "STB",
                    "message": "ValueError: final exc",
                },
            ],
        )
        for m in msgs:
            print(m)

        if OPEN_IN_BROWSER:
            import webbrowser

            webbrowser.open(log_target.as_uri())
