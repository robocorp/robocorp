# TODO: don't let playwright print directly into stdout, it's breaking console behaviour
import platform
from pathlib import Path
from typing import Literal

from playwright.sync_api import Browser, Page
from playwright.sync_api import sync_playwright as _sync_playwright


def _registry_path(browser: Literal["chrome", "firefox"]) -> str:
    if platform.system() == "Windows":
        import winreg

        location = winreg.HKEY_LOCAL_MACHINE
        browser_registry = (
            rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{browser}.exe"
        )
        key = winreg.OpenKeyEx(location, browser_registry)
        # empty string key gets the (Default) value
        path = winreg.QueryValueEx(key, "")
        if isinstance(path, tuple):
            path = path[0]
        assert path, f"Could not find {browser} path"
        return path
    raise RuntimeError("Not implemented for this OS")


EXECUTABLE_PATHS = {
    "chrome": {
        "Linux": "/usr/bin/google-chrome",
        "Darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    },
    "firefox": {
        "Linux": "/usr/bin/firefox",
        "Windows": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        "Darwin": "/Applications/Firefox.app/Contents/MacOS/firefox",
    },
}


def _get_executable_path(browser: Literal["firefox", "chrome"]) -> str:
    browser = browser.lower()
    system = platform.system()

    if system == "Windows":
        return _registry_path(browser)

    assert browser in EXECUTABLE_PATHS
    executable_path = EXECUTABLE_PATHS[browser][system]
    assert Path(executable_path).exists()

    return str(executable_path)


def open_browser(
    browser: Literal["firefox", "chrome"] = "chrome",
    headless=True
    # TODO: support more args
) -> Browser:
    """Launch a Playwright browser instance.

    Args:
        browser: Specifies which browser to use.
            Supported browsers are: ``chrome`` and ``firefox``.
        headless: If set to False a GUI is provided, otherwise it is hidden.

    Returns:
        Browser: A Browser instance.

    """
    playwright = _sync_playwright().start()

    assert playwright
    # TODO: allow user to also pass their own custom path?
    executable_path = _get_executable_path(browser)

    if browser == "chrome":
        browser = "chromium"

    launched_browser = playwright[browser].launch(
        executable_path=executable_path, headless=headless
    )
    return launched_browser


def open_url(url: str, headless=True) -> Page:
    """Launch a Playwright browser instance and opens the given URL.

    Note:
        Uses the ``chrome`` browser.

    Args:
        url: Navigates to the provided URL.
        headless: If set to False a GUI is provided, otherwise it is hidden.

    Returns:
        Page: A Page instance.

    """
    browser = open_browser(headless=headless)
    page = browser.new_page()
    page.goto(url)
    return page
