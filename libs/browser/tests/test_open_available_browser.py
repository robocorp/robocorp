import pytest

from robo.libs.browser.browser import open_browser, _get_executable_path


def test_get_executable_path():
    executable_path = _get_executable_path("chrome")
    assert executable_path

    executable_path = _get_executable_path("firefox")
    assert executable_path


@pytest.mark.skip(reason="no way of currently testing this")
def test_simple_page_actions():
    browser = open_browser(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("http://rpachallenge.com/")
    return page
