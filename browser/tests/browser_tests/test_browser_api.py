import os
from pathlib import Path


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
    from robocorp.browser import context, open_url, page

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

    another_page = open_url(page2_html.as_uri())
    assert another_page is not initial_page
    assert initial_page.is_closed()

    _check_page_query("Page2")
    assert page() is another_page


def test_get_executable_path():
    from robocorp.browser._browser_context import _get_executable_path

    executable_path = _get_executable_path("chrome")
    assert executable_path

    executable_path = _get_executable_path("firefox")
    assert executable_path


def test_screenshot_on_failure(datadir):
    from browser_tests.fixtures import robo_run
    from robocorp.log import verify_log_messages_from_log_html

    result = robo_run(["run"], returncode=1, cwd=datadir)
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
