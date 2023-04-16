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

HTML_MESSAGE = '<p>Image is: <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAApgAAAKYB3X3/OAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAANCSURBVEiJtZZPbBtFFMZ/M7ubXdtdb1xSFyeilBapySVU8h8OoFaooFSqiihIVIpQBKci6KEg9Q6H9kovIHoCIVQJJCKE1ENFjnAgcaSGC6rEnxBwA04Tx43t2FnvDAfjkNibxgHxnWb2e/u992bee7tCa00YFsffekFY+nUzFtjW0LrvjRXrCDIAaPLlW0nHL0SsZtVoaF98mLrx3pdhOqLtYPHChahZcYYO7KvPFxvRl5XPp1sN3adWiD1ZAqD6XYK1b/dvE5IWryTt2udLFedwc1+9kLp+vbbpoDh+6TklxBeAi9TL0taeWpdmZzQDry0AcO+jQ12RyohqqoYoo8RDwJrU+qXkjWtfi8Xxt58BdQuwQs9qC/afLwCw8tnQbqYAPsgxE1S6F3EAIXux2oQFKm0ihMsOF71dHYx+f3NND68ghCu1YIoePPQN1pGRABkJ6Bus96CutRZMydTl+TvuiRW1m3n0eDl0vRPcEysqdXn+jsQPsrHMquGeXEaY4Yk4wxWcY5V/9scqOMOVUFthatyTy8QyqwZ+kDURKoMWxNKr2EeqVKcTNOajqKoBgOE28U4tdQl5p5bwCw7BWquaZSzAPlwjlithJtp3pTImSqQRrb2Z8PHGigD4RZuNX6JYj6wj7O4TFLbCO/Mn/m8R+h6rYSUb3ekokRY6f/YukArN979jcW+V/S8g0eT/N3VN3kTqWbQ428m9/8k0P/1aIhF36PccEl6EhOcAUCrXKZXXWS3XKd2vc/TRBG9O5ELC17MmWubD2nKhUKZa26Ba2+D3P+4/MNCFwg59oWVeYhkzgN/JDR8deKBoD7Y+ljEjGZ0sosXVTvbc6RHirr2reNy1OXd6pJsQ+gqjk8VWFYmHrwBzW/n+uMPFiRwHB2I7ih8ciHFxIkd/3Omk5tCDV1t+2nNu5sxxpDFNx+huNhVT3/zMDz8usXC3ddaHBj1GHj/As08fwTS7Kt1HBTmyN29vdwAw+/wbwLVOJ3uAD1wi/dUH7Qei66PfyuRj4Ik9is+hglfbkbfR3cnZm7chlUWLdwmprtCohX4HUtlOcQjLYCu+fzGJH2QRKvP3UNz8bWk1qMxjGTOMThZ3kvgLI5AzFfo379UAAAAASUVORK5CYII="></p>'


def test_log_html_features(tmpdir) -> None:
    """
    This is a test which should generate an output for a log.html which
    showcases all the features available.
    """
    from robo_log import Filter, FilterKind, verify_log_messages_from_log_html

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

    __tracebackhide__ = 1

    log_target = Path(tmpdir.join("log.html"))

    with robo_log.setup_auto_logging(
        filters=[
            Filter("difflib", FilterKind.log_on_project_call),
        ]
    ):
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
            robo_log.start_task("Setup", "setup", str(tmpdir), 0, [])
            import difflib

            difflib = reload(difflib)

            diff = difflib.ndiff("aaaa bbb ccc ddd".split(), "aaaa bbb eee ddd".split())
            "".join(diff)
            robo_log.end_task("Setup", "setup", "PASS", "end msg")

            robo_log.start_run("Test Log HTML Features")
            robo_log.start_task("my_task", "modname", str(tmpdir), 0, [])

            for _i in range(2):
                check.some_method()
                robo_log.critical("Some log error")
                robo_log.warn("Some log warn")
                robo_log.info("Some log info")
                HTML_MESSAGE_LINENO = sys._getframe().f_lineno + 1
                robo_log.info(HTML_MESSAGE, html=True)
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

            robo_log.end_task(
                "my_task",
                "modname",
                "ERROR",
                "Marking that it exited with error due to some reason...",
            )
            robo_log.end_run("Test Log HTML Features", "PASS")

        assert log_target.exists()

        msgs = verify_log_messages_from_log_html(
            log_target,
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
                    "source": __file__,
                },
                {
                    "message_type": "LH",
                    "level": "I",
                    "message": HTML_MESSAGE,
                    "source": __file__,
                    "lineno": HTML_MESSAGE_LINENO,
                },
                {
                    "message_type": "STB",
                    "message": "RuntimeError: initial exc",
                },
                {
                    "message_type": "STB",
                    "message": "ValueError: final exc",
                },
                {
                    "message_type": "T",
                    # i.e.: check for the utc timezone (+00:00) in the time.
                    "__check__": lambda msg: msg["initial_time"].endswith("+00:00"),
                },
                {
                    "message_type": "SE",
                    "name": "another_method",
                    "libname": "robo_log_tests._resources.check_traceback",
                    "type": "METHOD",
                },
            ],
        )
        for m in msgs:
            print(m)

        if OPEN_IN_BROWSER:
            import webbrowser

            webbrowser.open(log_target.as_uri())
