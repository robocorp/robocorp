import sys
from typing import Dict

import pytest
from devutils.fixtures import RobocorpTaskRunner


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
            from robocorp.browser._context import browser_context_kwargs

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


def test_screenshot_on_failure(datadir, robocorp_task_runner: RobocorpTaskRunner):
    from robocorp.log import verify_log_messages_from_log_html

    robocorp_task_runner.run_tasks(["run"], returncode=1, cwd=datadir)
    log_html = robocorp_task_runner.log_html
    assert log_html
    verify_log_messages_from_log_html(log_html, [{"message_type": "LH"}])


def test_browser_type_launch_args(clear_session_caches, monkeypatch):
    import os

    from robocorp import browser
    from robocorp.browser._context import browser_type_launch_args

    default_headless = False
    if sys.platform.startswith("linux"):
        default_headless = not (
            os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
        )

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


def test_close_with_multiple_pages(pyfile, datadir):
    from devutils.fixtures import robocorp_tasks_run
    from robocorp.log import verify_log_messages_from_log_html

    @pyfile
    def task_pyfile_run_tasks():
        from robocorp import browser, tasks

        @tasks.task
        def check_close_multiple_pages() -> None:
            browser.page()
            browser.context().new_page()

    robocorp_tasks_run(["run", task_pyfile_run_tasks], returncode=0, cwd=datadir)
    log_html = datadir / "output" / "log.html"
    assert log_html.exists()
    verify_log_messages_from_log_html(
        log_html,
        [
            {"message_type": "ST", "name": "check_close_multiple_pages"},
            {"message_type": "ET", "status": "PASS"},
        ],
    )


@pytest.fixture
def restore_curdir():
    import os

    curdir = os.path.abspath(".")
    yield
    os.chdir(curdir)


def test_persistent_context(datadir, pyfile, restore_curdir) -> None:
    import os

    from robocorp.log import verify_log_messages_from_log_html

    os.chdir(datadir)

    @pyfile
    def task_pyfile_run_tasks():
        import os  # noqa
        import time

        from robocorp import browser, tasks

        new_cookie = {
            "name": "PERSISTENT_COOKIE_CHECK",
            "value": "PERSISTENT_COOKIE_CHECK_VALUE",
            "domain": "MY_DOMAIN",
            "path": "/",
            "expires": time.time() + 10000000,
            "httpOnly": True,
            "secure": False,
            "sameSite": "Strict",
        }

        @tasks.task
        def add_to_cookies():
            from pathlib import Path

            browser.configure(
                persistent_context_directory=os.environ["USE_PERSISTENT_DIR"]
            )
            browser.context().add_cookies([new_cookie])
            uri1 = Path("page1.html").absolute().as_uri()
            uri2 = Path("page2.html").absolute().as_uri()

            browser.page().goto(uri1)
            browser.context().new_page().goto(uri2)

        @tasks.task
        def check_cookies() -> None:
            cookies = browser.context().cookies()
            for cookie in cookies:
                if cookie["name"] == "PERSISTENT_COOKIE_CHECK":
                    break
            else:
                raise AssertionError(
                    f"Did not find PERSISTENT_COOKIE_CHECK cookie. Found: {cookies}"
                )

            # Pages themselves are not restored (but a default blank one is
            # always created).
            assert len(browser.context().pages) == 1

            assert browser.page() is browser.context().pages[0]
            assert len(browser.context().pages) == 1

    from devutils.fixtures import robocorp_tasks_run

    additional_env: Dict[str, str] = {
        "USE_PERSISTENT_DIR": str(datadir / "persistent_dir"),
    }

    robocorp_tasks_run(
        ["run", task_pyfile_run_tasks],
        returncode=0,
        cwd=datadir,
        additional_env=additional_env,
    )
    log_html = datadir / "output" / "log.html"
    assert log_html.exists()
    verify_log_messages_from_log_html(
        log_html,
        [
            {"message_type": "ST", "name": "add_to_cookies"},
            {"message_type": "ST", "name": "check_cookies"},
            {"message_type": "ET", "status": "PASS"},
            {"message_type": "ET", "status": "PASS"},
        ],
    )
