from enum import Enum

from playwright.sync_api import Error


class BrowserNotFound(Error):
    """No matching browser found in the environment."""


class InstallError(RuntimeError):
    """Error encountered during browser install"""


class BrowserEngine(str, Enum):
    """Valid browser engines for Playwright."""

    CHROMIUM = "chromium"
    CHROME = "chrome"
    CHROME_BETA = "chrome-beta"
    MSEDGE = "msedge"
    MSEDGE_BETA = "msedge-beta"
    MSEDGE_DEV = "msedge-dev"
    FIREFOX = "firefox"
    WEBKIT = "webkit"
