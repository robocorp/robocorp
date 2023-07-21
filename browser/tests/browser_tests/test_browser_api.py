import sys

import pytest


@pytest.fixture(autouse=True)
def clear_session_caches():
    from robocorp.tasks._hooks import after_all_tasks_run

    after_all_tasks_run([])
    yield lambda: after_all_tasks_run([])
    after_all_tasks_run([])


def test_browser_api(datadir, pyfile) -> None:
    """
    Note: because we mess with the session/task caches in tests for tests which
    actually spawn a new page a subprocess should be used.

    The code below will create a temporary file with the method contents
    and then it'll use robocorp.tasks to run it.
    """
    from robocorp.log import verify_log_messages_from_log_html

    @pyfile
    def task_pyfile_run_tasks():
        from robocorp import tasks

        def _check_page_query(page_prefix):
            from robocorp import browser

            found = set(
                str(selector.text_content()).strip()
                for selector in browser.page().query_selector_all(".label")
            )
            assert found == {
                f"{page_prefix}:Div1 label contents",
                f"{page_prefix}:Div2 label contents",
            }

        @tasks.task
        def check_browser_api() -> None:
            from pathlib import Path

            from robocorp.browser import context, goto, page

            initial_page = page()
            page1_html: Path = Path("page1.html").absolute()
            page2_html: Path = Path("page2.html").absolute()

            initial_page.goto(page1_html.as_uri())
            _check_page_query("Page1")

            assert page() is initial_page

            new_page = context().new_page()
            assert new_page is not initial_page
            new_page.close()

            # If the current page is closed another one is automatically provided.
            page().close()

            another_page = goto(page2_html.as_uri())
            assert another_page is not initial_page
            assert initial_page.is_closed()

            _check_page_query("Page2")
            assert page() is another_page

        @tasks.task
        def check_browser_viewport() -> None:
            import os
            from pathlib import Path

            from robocorp.browser import configure, configure_context, page
            from robocorp.browser._browser_context import browser_context_kwargs

            assert "viewport" not in browser_context_kwargs()
            configure(viewport_size=(755, 600))
            configure_context(ignore_https_errors=True)

            assert browser_context_kwargs()["viewport"] == {"width": 755, "height": 600}
            assert browser_context_kwargs()["ignore_https_errors"]

            p = page()

            p.goto((Path(os.path.abspath("page3.html"))).as_uri())
            assert p.viewport_size == {"width": 755, "height": 600}

    from devutils.fixtures import robocorp_tasks_run

    robocorp_tasks_run(["run", task_pyfile_run_tasks], returncode=0, cwd=datadir)
    log_html = datadir / "output" / "log.html"
    assert log_html.exists()
    verify_log_messages_from_log_html(
        log_html,
        [
            {"message_type": "ST", "name": "check_browser_viewport"},
            {"message_type": "ST", "name": "check_browser_api"},
            {"message_type": "ET", "status": "PASS"},
            {"message_type": "ET", "status": "PASS"},
        ],
    )


def test_screenshot_on_failure(datadir):
    import os

    from devutils.fixtures import robocorp_tasks_run
    from robocorp.log import verify_log_messages_from_log_html

    result = robocorp_tasks_run(["run"], returncode=1, cwd=datadir)
    decoded = result.stdout.decode("utf-8", "replace")
    assert "RuntimeError: Some error..." in decoded
    log_html = datadir / "output" / "log.html"
    if not log_html.exists():
        msg = f"\n{log_html} does not exist.\n"

        if not datadir.exists():
            msg += f"\n{datadir} does not exists.\n"
        else:
            msg += f"\n{datadir} exists.\nContents: {os.listdir(datadir)}\n"

            output_dir = datadir / "output"
            if not output_dir.exists():
                msg += f"\n{output_dir} does not exists.\n"
            else:
                msg += f"\n{output_dir} exists.\nContents: {os.listdir(output_dir)}\n"

        msg += f"\nStdout:\n{decoded}"

        raise AssertionError(msg)
    verify_log_messages_from_log_html(log_html, [{"message_type": "LH"}])


def test_browser_type_launch_args(clear_session_caches, monkeypatch):
    import os

    from robocorp import browser
    from robocorp.browser._browser_context import browser_type_launch_args

    default_headless = not os.environ.get(
        "GITHUB_ACTIONS_MATRIX_NAME"
    ) and sys.platform.startswith("linux")

    assert browser_type_launch_args()["headless"] is default_headless

    clear_session_caches()
    monkeypatch.setenv("RPA_HEADLESS_MODE", "1")
    assert browser_type_launch_args()["headless"] is True

    clear_session_caches()
    monkeypatch.setenv("RPA_HEADLESS_MODE", "0")
    assert browser_type_launch_args()["headless"] is False

    clear_session_caches()
    monkeypatch.delenv("RPA_HEADLESS_MODE")
    assert browser_type_launch_args()["headless"] is default_headless

    clear_session_caches()
    browser.configure(headless=True)
    assert browser_type_launch_args()["headless"] is True

    clear_session_caches()
    browser.configure(headless=False)
    assert browser_type_launch_args()["headless"] is False

    clear_session_caches()
    browser.configure(headless=None)
    assert browser_type_launch_args()["headless"] is default_headless
