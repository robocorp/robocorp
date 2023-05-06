from robocorp.browser.browser import open_browser, open_url
from typing import Optional
from ._browser_context import _PlayWrightBrowserContext
from playwright.sync_api import (
    Browser,
    BrowserContext,
    BrowserType,
    Error,
    Page,
    Playwright,
    sync_playwright,
)

_global_browser_context: Optional[_PlayWrightBrowserContext]


def initialize(
    browser_engine="chrome",
    headless: Optional[bool] = None,
    slowmo: int = 0,
    tracing: str = "off",
    video: str = "off",
    screenshot: str = "off",
) -> None:
    """
    This method may be called before any other method to initialize the
    context for the browser.

    Calling this method is optional (note that it may be implicitly called
    by any other method which expects to interact a browser and calling it
    afterwards will throw an error).

    Args:
        browser_engine:
            help="Browser engine which should be used",
            choices=["chrome", "chromium", "firefox", "webkit"],

        headless:
            Run headless or not.

        slowmo:
            Run interactions in slow motion.

        tracing:
            default="off",
            choices=["on", "off", "retain-on-failure"],
            help="Whether to record a trace for each task.",

        video:
            default="off",
            choices=["on", "off", "retain-on-failure"],
            help="Whether to record video for each task.",

        screenshot:
            default="off",
            choices=["on", "off", "only-on-failure"],
            help="Whether to automatically capture a screenshot after each task.",
    """
    global _global_browser_context
    if _global_browser_context is not None:
        raise RuntimeError(
            "The browser is already initialized. It's not possible to reinitialize it."
        )
    if browser_engine == "chrome":
        browser_engine = "chromium"
    if browser_engine not in ["chrome", "chromium", "firefox", "webkit"]:
        raise ValueError(f"Invalid browser_engine: {browser_engine}")

    _global_browser_context = _PlayWrightBrowserContext(
        browser_engine, headless, slowmo, tracing, video, screenshot
    )

    def call_after_tasks_run(*args, **kwargs):
        # Reset the context when all tasks finish running.
        global _global_browser_context
        _global_browser_context = None
        after_all_tasks_run.unregister(call_after_tasks_run)

    after_all_tasks_run.register(call_after_tasks_run)


def _obtain_browser_context() -> _PlayWrightBrowserContext:
    if _global_browser_context is None:
        initialize()
    ret = _global_browser_context
    assert ret is not None
    return ret


def _page() -> Page:
    """
    Provides the browser page to interact with.

    Note that after a page is created, the same page is returned until the
    current task finishes.

    If a new page is required use:

    from robocorp import browser
    page = browser.context.new_page()
    """
    return _obtain_browser_context().page


def _browser() -> Browser:
    return _obtain_browser_context().browser


def _playwright() -> Playwright:
    return _obtain_browser_context().playwright


def _context() -> BrowserContext:
    return _obtain_browser_context().context


_name_to_property = {
    "page": _page,
    "browser": _browser,
    "playwright": _playwright,
    "context": _context,
}


def __getattr__(name):
    """
    Unfortunately we don't have @property for modules, so, __getattr__
    is a workaround so that we have some API such as:

    from robocorp import browser
    page = browser.page
    """
    try:
        prop = _name_to_property[name]
    except KeyError:
        raise AttributeError(f"No attribute named: {name}")
    return prop()


# --- Public API
# Gotten with __getattr__ by calling the proper method.
page: Page
browser: Browser
playwright: Playwright
context: BrowserContext
