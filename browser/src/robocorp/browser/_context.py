import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator, Optional, Union

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
    config = browser_config()

    # Make sure playwright searches from robocorp-specific path
    path = browsers_path(isolated=config.isolated)
    log.debug(f"Playwright browsers path: {path})")
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(path)

    pw = sync_playwright().start()
    yield pw
    if config.skip_playwright_stop:
        # Just skip the playwright stop in this case. Usually not recommended,
        # but can be coupled with an early os._exit under really specific
        # conditions.
        pass
    else:
        pw.stop()


@session_cache
def _browser_type() -> BrowserType:
    pw = playwright()

    engine = browser_config().browser_engine
    klass, _ = ENGINE_TO_ARGS[engine]

    return getattr(pw, klass)


@session_cache
def _browser_launcher() -> Callable[..., Union[Browser, BrowserContext]]:
    """
    If a persistent_context_directory is requested, playwright doesn't really
    have an API to provide a `Browser`, just a `BrowserContext` (it opens with
    a default blank page by default), so, in this case we have to deal with
    both returns (the regular browser() api will throw an error if that's the
    case -- that's backward compatible because this would never happen
    before the `persistent_context_directory` configuration option was available).
    """
    config = browser_config()
    browser_type: BrowserType = _browser_type()

    def launch(**kwargs: dict[str, Any]) -> Union[Browser, BrowserContext]:
        launch_options = {**browser_type_launch_args(), **kwargs}

        if "channel" not in launch_options:
            _, channel = ENGINE_TO_ARGS[config.browser_engine]
            if channel is not None:
                launch_options["channel"] = channel

        persistent_context_directory = __persistent_context_directory()
        try:
            if persistent_context_directory is None:
                return browser_type.launch(**launch_options)
            else:
                # launch_persistent_context is a mixture of the launch + context,
                # so, in this case we use both here.
                launch_options.update(browser_context_kwargs())
                ctx = browser_type.launch_persistent_context(
                    persistent_context_directory, **launch_options
                )
                return ctx
        except Error as err:
            if "executable doesn't exist" not in err.message.lower():
                raise
            install_path = browsers_path(isolated=config.isolated)
            raise BrowserNotFound(
                f"No matching browser found ({install_path})"
            ) from err

    return launch


@session_cache
def __persistent_context_directory() -> Optional[Union[str, Path]]:
    # After queried once it cannot change anymore (so, be careful with it).
    return browser_config().persistent_context_directory


def __launch_browser_or_context(
    check_install: bool, **kwargs
) -> Union[Browser, BrowserContext]:
    """
    Note: this is not directly cached, but it should be called from
    functions which are `session_cache` or `task_cache` themselves.

    Args:
        check_install: Flag which determines whether we should install the
        browser if it's not available.
    """
    config = browser_config()
    launcher = _browser_launcher()

    if check_install and config.install:
        install_browser(engine=config.browser_engine, isolated=config.isolated)

    try:
        return launcher(**kwargs)
    except BrowserNotFound:
        if not check_install:
            raise

        if config.install is not None:
            raise

    # If we reached here we must check whether the browser was installed.
    install_browser(engine=config.browser_engine, isolated=config.isolated)
    return launcher(**kwargs)


@session_cache
def browser(**kwargs) -> Iterator[Browser]:
    """
    The kwargs are passed as additional launch options to the
    BrowserType.launch(**kwargs).
    """
    if __persistent_context_directory() is not None:
        raise RuntimeError(
            "This API is not available when launching a persistent context. "
            "Please use the `context` instead."
        )

    browser = __launch_browser_or_context(True, **kwargs)
    if not isinstance(browser, Browser):
        raise AssertionError(
            f"When not using a persistent context directory a Browser is expected here."
            f" Found: {type(browser)} ({browser})."
        )

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


@dataclass
class _State:
    # With a persistent context we have to check the install on the
    # first call, but not on subsequent ones.
    check_install: bool = True


@session_cache
def __state():
    # Helper to provide the state given a session.
    return _State()


@task_cache
def context(**kwargs) -> Iterator[BrowserContext]:
    from robocorp.tasks import get_current_task

    if __persistent_context_directory() is None:
        all_kwargs: dict = {}
        all_kwargs.update(**browser_context_kwargs())
        all_kwargs.update(**kwargs)

        ctx = browser().new_context(**all_kwargs)
    else:
        state = __state()
        check_install = state.check_install
        state.check_install = False  # On subsequent calls we shouldn't check it.
        browser_or_context = __launch_browser_or_context(check_install, **kwargs)
        ctx = browser_or_context

    yield ctx

    try:
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

            for p in ctx.pages:
                if not p.is_closed():
                    try:
                        screenshot(p, log_level="ERROR" if failed else "INFO")
                    except Error:
                        pass
    finally:
        ctx.close()


@task_cache
def page() -> Page:
    ctx: BrowserContext = context()

    current_pages = ctx.pages
    if len(current_pages) > 0:
        # On the case where the persistent_context_directory is specified
        # playwright automatically creates an empty page, so, provide it
        # by default.
        p = current_pages[0]
    else:
        p = ctx.new_page()

    # When the page is closed we automatically clear the cache.
    p.on("close", lambda *args: page.clear_cache())
    return p
