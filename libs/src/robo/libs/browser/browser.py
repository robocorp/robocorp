from pathlib import Path
import platform
from typing import Literal

from playwright.sync_api import Browser, sync_playwright as _sync_playwright

EXECUTABLE_PATHS = {
    "chromium": {
        "Linux": "/usr/bin/chromium-browser",
        "Windows": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "Darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    },
    "firefox": {
        "Linux": "/usr/bin/firefox",
        "Windows": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        "Darwin": "/Applications/Firefox.app/Contents/MacOS/firefox",
    },
}


def _get_executable_path(browser: Literal["firefox", "chromium"]) -> str:
    system = platform.system()
    assert browser in EXECUTABLE_PATHS
    executable_path = EXECUTABLE_PATHS[browser][system]
    assert Path(executable_path).exists()
    return executable_path


def open_available_browser(
    browser: Literal["firefox", "chromium"] = "chromium",
    headless=True
    # TODO: support more args
) -> Browser:
    playwright = _sync_playwright().start()

    assert playwright
    # TODO: allow user to also pass their own custom path?
    executable_path = _get_executable_path(browser)

    launched_browser = playwright[browser].launch(
        executable_path=executable_path, headless=headless
    )
    return launched_browser


#     Open Available Browser    http://rpachallenge.com/


# Close All Browsers


#  Click Button    Start


# Input Text    alias:First Name    ${person}[First Name]


# Capture Element Screenshot    alias:Congratulations
