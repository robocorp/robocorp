import platform
import sys
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Literal, Optional

from playwright.sync_api import (
    Browser,
    BrowserContext,
    BrowserType,
    Error,
    Page,
    Playwright,
    sync_playwright,
)
from robocorp.tasks import session_cache, task_cache

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
    system = platform.system()

    if system == "Windows":
        return _registry_path(browser)

    if browser not in EXECUTABLE_PATHS:
        raise ValueError(f"Unsupported browser: {browser}")

    path = EXECUTABLE_PATHS[browser][system]
    if not Path(path).exists():
        raise RuntimeError(f"Browser executable not found: {path}")

    return path


def _registry_path(browser: Literal["chrome", "firefox"]) -> str:
    if sys.platform != "win32":
        raise NotImplementedError("Not implemented for non-Windows")

    import winreg

    parent = winreg.HKEY_LOCAL_MACHINE
    key = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{browser}.exe"

    handle = winreg.OpenKeyEx(parent, key)
    path, _ = winreg.QueryValueEx(handle, "")  # Empty string is (Default) value

    if not path:
        raise RuntimeError(f"Failed to read browser path: {browser}")

    return str(path)


class _BrowserConfig:
    __slots__ = "_browser_engine _headless _slowmo _screenshot __weakref__".split()

    def __init__(
        self,
        browser_engine: str = "chrome",
        headless: Optional[bool] = None,
        slowmo: int = 0,
        screenshot: str = "only-on-failure",
    ):
        """
        Args:
            browser_engine:
                help="Browser engine which should be used",
                choices=["chrome", "firefox"],

            headless:
                Run headless or not.

            slowmo:
                Run interactions in slow motion (number in millis).

            screenshot:
                default="only-on-failure",
                choices=["on", "off", "only-on-failure"],
                help="Whether to automatically capture a screenshot after each task.",
        """
        self.browser_engine = browser_engine
        self.headless = headless
        self.slowmo = slowmo
        self.screenshot = screenshot

    @property
    def browser_engine(self) -> str:
        return self._browser_engine

    @browser_engine.setter
    def browser_engine(self, value: str):
        assert value in ["chrome", "firefox"]
        self._browser_engine = value

    @property
    def headless(self) -> Optional[bool]:
        return self._headless

    @headless.setter
    def headless(self, value: Optional[bool]):
        assert value is None or isinstance(value, bool)
        self._headless = value

    @property
    def slowmo(self) -> int:
        return self._slowmo

    @slowmo.setter
    def slowmo(self, value: int):
        assert isinstance(value, int)
        assert value >= 0
        self._slowmo = value

    @property
    def screenshot(self) -> str:
        return self._screenshot

    @screenshot.setter
    def screenshot(self, value: str):
        assert value in ["on", "off", "only-on-failure"]
        self._screenshot = value


@session_cache
def _browser_config() -> _BrowserConfig:
    """
    The configuration used. Can be mutated as needed until
    `browser_context_args` is called (at which point mutating it will raise an
    error since it was already used).
    """
    return _BrowserConfig()


def _is_debugger_attached() -> bool:
    pydevd = sys.modules.get("pydevd")
    if not pydevd or not hasattr(pydevd, "get_global_debugger"):
        return False
    debugger = pydevd.get_global_debugger()
    if not debugger or not hasattr(debugger, "is_attached"):
        return False
    return debugger.is_attached()


@session_cache
def browser_type_launch_args() -> Dict:
    launch_options = {}
    headless = _browser_config().headless
    if headless is None:
        launch_options["headless"] = not _is_debugger_attached()
    else:
        launch_options["headless"] = headless

    slowmo_option = _browser_config().slowmo
    if slowmo_option:
        launch_options["slow_mo"] = slowmo_option
    return launch_options


@session_cache
def playwright() -> Iterator[Playwright]:
    pw = sync_playwright().start()
    yield pw
    # Need to stop when tasks finish running.
    pw.stop()


@session_cache
def _browser_type() -> BrowserType:
    pw = playwright()

    engine = _browser_config().browser_engine
    if engine == "chrome":
        engine = "chromium"

    return getattr(pw, engine)


@session_cache
def _browser_launcher() -> Callable[..., Browser]:
    browser_type: BrowserType = _browser_type()

    def launch(**kwargs: Dict) -> Browser:
        launch_options = {**browser_type_launch_args(), **kwargs}

        if "executable_path" not in launch_options:
            engine = _browser_config().browser_engine
            launch_options["executable_path"] = _get_executable_path(engine)

        browser = browser_type.launch(**launch_options)
        return browser

    return launch


@session_cache
def browser(**kwargs) -> Iterator[Browser]:
    """
    The kwargs are passed as additional launch options to the
    BrowserType.launch(**kwargs).
    """
    # Note: one per session (must be tear-down).
    launcher = _browser_launcher()
    browser = launcher(**kwargs)
    yield browser
    browser.close()


@task_cache
def context(**browser_context_kwargs) -> Iterator[BrowserContext]:
    from robocorp.tasks import get_current_task

    pages: List[Page] = []
    ctx = browser().new_context(**browser_context_kwargs)
    ctx.on("page", lambda page: pages.append(page))

    yield ctx

    task = get_current_task()
    failed = False
    if task is not None:
        failed = task.failed

    screenshot_option = _browser_config().screenshot
    capture_screenshot = screenshot_option == "on" or (
        failed and screenshot_option == "only-on-failure"
    )
    if capture_screenshot:
        from robocorp.browser import screenshot

        for p in pages:
            if not p.is_closed():
                try:
                    screenshot(p, log_level="ERROR" if failed else "INFO")
                except Error:
                    pass

    ctx.close()


@task_cache
def page() -> Page:
    ctx: BrowserContext = context()
    p = ctx.new_page()

    # When the page is closed we automatically clear the cache.
    p.on("close", lambda *args: page.clear_cache())
    return p
