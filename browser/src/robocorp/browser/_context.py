import os
import sys
from typing import Any, Callable, Iterator

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

from robocorp import log

from ._config import browser_config
from ._engines import ENGINE_TO_ARGS, browsers_path, install_browser
from ._types import BrowserNotFound


def _get_auto_headless_state() -> bool:
    # If in Linux and with no valid display, we can assume we are in a
    # container which doesn't support UI.
    return sys.platform.startswith("linux") and not (
        os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")
    )


@session_cache
def browser_type_launch_args() -> dict[str, Any]:
    launch_options = {}

    # RPA_HEADLESS_MODE can be used to force whether running headless.
    rpa_headless_mode = os.environ.get("RPA_HEADLESS_MODE")
    if rpa_headless_mode is not None:
        launch_options["headless"] = bool(int(os.environ["RPA_HEADLESS_MODE"]))
    else:
        headless = browser_config().headless
        if headless is None:
            # Heuristic is now: run showing UI (headless=False) by default
            # and run headless when in a VM without a display.
            launch_options["headless"] = _get_auto_headless_state()
        else:
            launch_options["headless"] = headless

    slowmo_option = browser_config().slowmo
    if slowmo_option:
        launch_options["slow_mo"] = slowmo_option
    return launch_options


@session_cache
def playwright() -> Iterator[Playwright]:
    import asyncio

    config = browser_config()

    # Make sure playwright searches from robocorp-specific path
    path = browsers_path(isolated=config.isolated)
    log.debug(f"Playwright browsers path: {path})")
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(path)

    pw = sync_playwright().start()
    yield pw
    loop = asyncio.get_running_loop()

    def _stop_loop():
        loop.stop()

    # Fix for https://github.com/microsoft/playwright-python/issues/2135
    # (where playwright gets stuck on pw.stop()).
    loop.call_later(2, _stop_loop)
    try:
        pw.stop()
    except Exception as e:
        # This could happen in theory if there's some upcoming item scheduled
        # to run later which still hasn't run (for us, at teardown, this is Ok,
        # we don't want to fail due to that).
        log.exception(
            f"Ignoring Exception raised when finishing playwright and "
            f"the asyncio loop: {e}"
        )


@session_cache
def _browser_type() -> BrowserType:
    pw = playwright()

    engine = browser_config().browser_engine
    klass, _ = ENGINE_TO_ARGS[engine]

    return getattr(pw, klass)


@session_cache
def _browser_launcher() -> Callable[..., Browser]:
    config = browser_config()
    browser_type: BrowserType = _browser_type()

    def launch(**kwargs: dict[str, Any]) -> Browser:
        launch_options = {**browser_type_launch_args(), **kwargs}

        if "channel" not in launch_options:
            _, channel = ENGINE_TO_ARGS[config.browser_engine]
            if channel is not None:
                launch_options["channel"] = channel

        try:
            return browser_type.launch(**launch_options)
        except Error as err:
            if "executable doesn't exist" not in err.message.lower():
                raise
            install_path = browsers_path(isolated=config.isolated)
            raise BrowserNotFound(
                f"No matching browser found ({install_path})"
            ) from err

    return launch


@session_cache
def browser(**kwargs) -> Iterator[Browser]:
    """
    The kwargs are passed as additional launch options to the
    BrowserType.launch(**kwargs).
    """
    # Note: one per session (must be tear-down).
    config = browser_config()
    launcher = _browser_launcher()

    if config.install:
        install_browser(engine=config.browser_engine, isolated=config.isolated)

    try:
        browser = launcher(**kwargs)
    except BrowserNotFound:
        browser = None
        if config.install is not None:
            raise

    if browser is None:
        install_browser(engine=config.browser_engine, isolated=config.isolated)
        browser = launcher(**kwargs)

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

    pages: list[Page] = []
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

    screenshot_option = browser_config().screenshot
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
