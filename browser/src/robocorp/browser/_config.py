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

            isolated:
                Whether to store downloaded browser engines inside the isolated
                environment, or in a global cache
        """  # noqa
        self.browser_engine = browser_engine
        self.install = install
        self.headless = headless
        self.slowmo = slowmo
        self.screenshot = screenshot
        self.isolated = isolated

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


@session_cache
def browser_config() -> _BrowserConfig:
    return _BrowserConfig()
