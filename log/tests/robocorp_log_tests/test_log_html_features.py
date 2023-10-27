import sys

HTML_MESSAGE = '<p>Image is: <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAnBAMAAACGbbfxAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAbUExURR4nOzpCVI+Tnf///+Pk5qqutXN4hVZdbMbJzod39mUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAETSURBVDjLnZIxT8MwFITPqDQdG1rBGjX8AOBS0hG1ghnUhbFSBlZvMFbqH+fZaeMLBJA4KZHzyb7ce374l1we3vm0Ty/Ix7era1YvSjOeVBWCZx3mveBDwlWyH1OUXM5t0yJqS+4V33xdwWFCrvOoOfmA1r30Z+r9jHV7zmeKd7ADQEOvATkFlzGz13JqIGanYbexYLOldcY+IsniqrEyRrUj7xBwccRm/lSuPqysI3YBjzUfQproNOr/0tLEgE3CK8P2YG54K401XIeWHDw2Uo5H5UP1l1ZXr9+7U2ffRfhTC9HwFVMmqOzl7vTDnEwSvhXsNLaoGbIGurvf97ArhzYbj01sm6TKXm3yC3yX8/hdwCdipl9ujxriXgAAAABJRU5ErkJggg=="></p>'


def test_log_html_features(tmpdir, ui_regenerate) -> None:
    """
    This is a test which should generate an output for a log.html which
    showcases all the features available.
    """
    from importlib import reload
    from pathlib import Path

    from robocorp_log_tests._resources import (
        check,
        check_iterators,
        check_sensitive_data,
        check_traceback,
    )

    from robocorp import log
    from robocorp.log import (
        DefaultAutoLogConfig,
        Filter,
        FilterKind,
        verify_log_messages_from_log_html,
    )

    __tracebackhide__ = 1

    log_target = Path(tmpdir.join("log.html"))

    with log.setup_auto_logging(
        DefaultAutoLogConfig(
            filters=[
                Filter("difflib", FilterKind.log_on_project_call),
            ]
        )
    ):
        check = reload(check)
        check_sensitive_data = reload(check_sensitive_data)
        check_traceback = reload(check_traceback)
        check_iterators = reload(check_iterators)

        with log.add_log_output(
            tmpdir,
            max_file_size="500kb",
            max_files=1,
            log_html=log_target,
            log_html_style=ui_regenerate.LOG_HTML_STYLE,
        ):
            log.start_task("Setup", "setup", str(tmpdir), 0)
            import difflib

            difflib = reload(difflib)

            diff = difflib.ndiff("aaaa bbb ccc ddd".split(), "aaaa bbb eee ddd".split())
            "".join(diff)
            log.end_task("Setup", "setup", "PASS", "end msg")

            log.start_run("Test Log HTML Features")
            log.start_task("my_task", "modname", str(tmpdir), 0)

            check.some_method()
            log.critical("Some log error", "value is", 1)
            log.warn("Some log warn")
            log.info("Some log info")
            HTML_MESSAGE_LINENO = sys._getframe().f_lineno + 1
            log.html(HTML_MESSAGE)
            check_sensitive_data.run()
            check_iterators.main()
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

            log.process_snapshot()

            log.end_task(
                "my_task",
                "modname",
                "ERROR",
                "Marking that it exited with error due to some reason...",
            )
            log.end_run("Test Log HTML Features", "ERROR")

        assert log_target.exists()

        def ends_with_timezone(msg):
            return msg["time"][-6:].startswith(("+", "-"))

        msgs = verify_log_messages_from_log_html(
            log_target,
            [
                {
                    "message_type": "L",
                    "level": "E",
                    "message": "Some log error value is 1",
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
                    "message": "ValueError: final exc (this exception occurred during handling of the previous exception)",
                },
                {
                    "message_type": "T",
                    # i.e.: check for the utc timezone (+00:00) in the time (actually, converted to local timezone)..
                    "__check__": ends_with_timezone,
                },
                {
                    "message_type": "SE",
                    "name": "another_method",
                    "libname": "robocorp_log_tests._resources.check_traceback",
                    "type": "METHOD",
                },
            ],
            [],
        )

        if ui_regenerate.PRINT_MESSAGES:
            for m in msgs:
                print(m)

        if ui_regenerate.OPEN_IN_BROWSER:
            import webbrowser

            webbrowser.open(log_target.as_uri())
