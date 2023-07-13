import os
import sys
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def clear_session_caches():
    from robocorp.tasks._hooks import after_all_tasks_run

    after_all_tasks_run([])
    yield lambda: after_all_tasks_run([])
    after_all_tasks_run([])


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


def test_browser_api(datadir) -> None:
    from robocorp.browser import context, goto, page

    initial_page = page()
    page1_html: Path = datadir / "page1.html"
    page2_html: Path = datadir / "page2.html"

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


def test_screenshot_on_failure(datadir):
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
