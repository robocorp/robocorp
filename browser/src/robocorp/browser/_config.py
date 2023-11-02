from pathlib import Path
from typing import Optional, Union

from robocorp.tasks import session_cache

from ._types import BrowserEngine


class _BrowserConfig:
    __slots__ = [
        "_browser_engine",
        "_install",
        "_headless",
        "_slowmo",
        "_screenshot",
        "_isolated",
        "_persistent_context_directory",
        "skip_playwright_stop",
        "__weakref__",
    ]

    def __init__(
        self,
        browser_engine: BrowserEngine = BrowserEngine.CHROMIUM,
        install: Optional[bool] = None,
        headless: Optional[bool] = None,
        slowmo: int = 0,
        screenshot: str = "only-on-failure",
        isolated: bool = False,
        persistent_context_directory: Optional[Union[str, Path]] = None,
        skip_playwright_stop: bool = False,
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

            headless: If set to False the browser UI will be shown. If set to True
                the browser UI will be kept hidden. If unset or set to None it'll
                show the browser UI only if a debugger is detected.

            slowmo:
                Run interactions in slow motion (number in millis).

            screenshot:
                Whether to automatically capture a screenshot after each task.
                default="only-on-failure"
                choices=["on", "off", "only-on-failure"]

            isolated:
                Used to define where the browser should be downloaded. If
                `True`, it'll be installed inside the isolated environment. If
                `False` (default) it'll be installed in a global cache folder.

            persistent_context_directory:
                If a persistent context should be used, this should be the
                directory in which the persistent context should be
                stored/loaded from (it can be used to store the state of the
                automation to allow for sessions and cookies to be reused in a
                new automation).

            skip_playwright_stop:
                Can be used to skip the playwright stop. Not recommended in
                general, only meant to be used to diagnose and workaround
                specific issues on the playwright stop coupled with an early
                os._exit shutdown in `robocorp-tasks`. Can cause a process leak
                and even a shutdown deadlock if used alone.
        """  # noqa
        self.browser_engine = browser_engine
        self.install = install
        self.headless = headless
        self.slowmo = slowmo
        self.screenshot = screenshot
        self.isolated = isolated
        self.persistent_context_directory = persistent_context_directory
        self.skip_playwright_stop = skip_playwright_stop

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

    @property
    def isolated(self) -> bool:
        return self._isolated

    @isolated.setter
    def isolated(self, value: bool):
        assert isinstance(value, bool)
        self._isolated = value

    @property
    def persistent_context_directory(self) -> Optional[Union[str, Path]]:
        return self._persistent_context_directory

    @persistent_context_directory.setter
    def persistent_context_directory(self, value: Optional[Union[str, Path]]):
        self._persistent_context_directory = value


@session_cache
def browser_config() -> _BrowserConfig:
    return _BrowserConfig()
