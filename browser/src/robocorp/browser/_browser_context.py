import os
import sys
from typing import Callable, Dict, Iterator, List, Optional, Union

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

from ._browser_engines import (
    ENGINE_TO_ARGS,
    BrowserEngine,
    browsers_path,
    install_browser,
)


class _BrowserConfig:
    __slots__ = [
        "_browser_engine",
        "_install",
        "_headless",
        "_slowmo",
        "_screenshot",
        "__weakref__",
    ]

    def __init__(
        self,
        browser_engine: BrowserEngine = BrowserEngine.CHROMIUM,
        install: Optional[bool] = None,
        headless: Optional[bool] = None,
        slowmo: int = 0,
        screenshot: str = "only-on-failure",
    ):
        """
        Args:
            browser_engine:
                Browser engine which should be used
                default="chromium"
                choices=["chromium", "chrome", "chrome-beta", "msedge",
                         "msedge-beta", "msedge-dev", "firefox", "webkit"]

            install:
                Install browser or not. If not defined, download is only
                attempted if the browser fails to launch.

            headless:
                Run headless or not.

            slowmo:
                Run interactions in slow motion (number in millis).

            screenshot:
                Whether to automatically capture a screenshot after each task.
                default="only-on-failure"
                choices=["on", "off", "only-on-failure"]
        """  # noqa
        self.browser_engine = browser_engine
        self.install = install
        self.headless = headless
        self.slowmo = slowmo
        self.screenshot = screenshot

    @property
    def browser_engine(self) -> BrowserEngine:
        return self._browser_engine

    @browser_engine.setter
    def browser_engine(self, value: Union[BrowserEngine, str]):
        self._browser_engine = BrowserEngine(value)

    @property
    def install(self) -> Optional[bool]:
        return self._install

    @install.setter
    def install(self, value: Optional[bool]):
        assert value is None or isinstance(value, bool)
        self._install = value

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


def _get_auto_headless_state() -> bool:
    # If in Linux and with no valid display, we can assume we are in a
    # container which doesn't support UI.
    return sys.platform.startswith("linux") and not (
        os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    )


@session_cache
def browser_type_launch_args() -> Dict:
    launch_options = {}

    # RPA_HEADLESS_MODE can be used to force whether running headless.
    rpa_headless_mode = os.environ.get("RPA_HEADLESS_MODE")
    if rpa_headless_mode is not None:
        launch_options["headless"] = bool(int(os.environ["RPA_HEADLESS_MODE"]))
    else:
        headless = _browser_config().headless
        if headless is None:
            # Heuristic is now: run showing UI (headless=False) by default
            # and run headless when in a VM without a display.
            launch_options["headless"] = _get_auto_headless_state()
        else:
            launch_options["headless"] = headless

    slowmo_option = _browser_config().slowmo
    if slowmo_option:
        launch_options["slow_mo"] = slowmo_option
    return launch_options


@session_cache
def playwright() -> Iterator[Playwright]:
    # Make sure playwright searches from robocorp-specific path
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_path())

    pw = sync_playwright().start()
    yield pw
    # Need to stop when tasks finish running.
    pw.stop()


@session_cache
def _browser_type() -> BrowserType:
    pw = playwright()

    engine = _browser_config().browser_engine
    klass, _ = ENGINE_TO_ARGS[engine]

    return getattr(pw, klass)


@session_cache
def _browser_launcher() -> Callable[..., Browser]:
    browser_type: BrowserType = _browser_type()

    def launch(**kwargs: Dict) -> Browser:
        launch_options = {**browser_type_launch_args(), **kwargs}

        if "channel" not in launch_options:
            engine = _browser_config().browser_engine
            _, channel = ENGINE_TO_ARGS[engine]
            if channel is not None:
                launch_options["channel"] = channel

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
    config = _browser_config()
    if config.install:
        install_browser(config.browser_engine)

    launcher = _browser_launcher()
    try:
        browser = launcher(**kwargs)
    except Error:
        if config.install is None:
            install_browser(config.browser_engine)
            browser = launcher(**kwargs)
        else:
            raise

    yield browser
    browser.close()


@session_cache
def browser_context_kwargs() -> dict:
    """
    The returned dict may be edited to change the arguments passed to
    `playwright.Browser.new_context`.

    Note:
        This is a (robocorp.tasks) session cache, so, the same dict will be
        returned over and over again.
    """
    return {}


@task_cache
def context(**kwargs) -> Iterator[BrowserContext]:
    from robocorp.tasks import get_current_task

    pages: List[Page] = []
    all_kwargs: dict = {}
    all_kwargs.update(**browser_context_kwargs())
    all_kwargs.update(**kwargs)
    ctx = browser().new_context(**all_kwargs)
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
