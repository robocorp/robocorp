import time
from typing import Iterator, List, Literal, Optional

from robocorp.windows._errors import ElementNotFound
from robocorp.windows._ui_automation_wrapper import _UIAutomationControlWrapper
from robocorp.windows._window_element import WindowElement
from robocorp.windows.protocols import Locator


def _iter_window_locators(locator: Locator) -> Iterator[Optional[Locator]]:
    assert locator, "Empty locator passed."

    if "type:" in locator or "control:" in locator:
        yield locator  # yields rigid string locator
    else:
        # yields flexible string locators with different types
        yield f"{locator} type:WindowControl"
        yield f"{locator} type:PaneControl"


def find_window(
    root_element: Optional[_UIAutomationControlWrapper],
    locator: Locator,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None,
    foreground: bool = True,
) -> WindowElement:
    from robocorp import windows

    config = windows.config()
    window_element: WindowElement
    locators = tuple(_iter_window_locators(locator))

    if timeout is None:
        timeout = config.timeout

    assert timeout is not None
    timeout /= len(locators)
    if wait_time is None:
        wait_time = config.wait_time

    for loc in locators:
        from robocorp.windows._find_ui_automation import find_ui_automation_wrapper

        try:
            element = find_ui_automation_wrapper(
                loc, search_depth, root_element=root_element, timeout=timeout
            )
            window_element = WindowElement(element)
        except ElementNotFound:
            continue
        else:
            if foreground:
                window_element.foreground_window()
            if wait_time:
                time.sleep(wait_time)
            return window_element

    # No matches.
    _raise_window_not_found(locator, timeout, root_element)
    raise AssertionError("Should never get here.")  # Just to satisfy typing.


def _raise_window_not_found(
    locator, timeout, root_element: Optional[_UIAutomationControlWrapper]
):
    from robocorp import windows

    config = windows.config()

    msg = (
        f"Could not locate window with locator: {locator!r} "
        f"(timeout: {timeout if timeout is not None else config.timeout})"
    )
    if config.verbose_errors:
        windows_msg = ["\nFound Windows:"]
        for w in find_windows(root_element, locator="regex:.*"):
            windows_msg.append(str(w))

        msg += "\n".join(windows_msg)
    raise ElementNotFound(msg)


def find_windows(
    root_element: Optional[_UIAutomationControlWrapper],
    locator: Locator,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_for_window: bool = False,
    search_strategy: Literal["siblings", "all"] = "all",
) -> List[WindowElement]:
    from robocorp import windows
    from robocorp.windows._find_ui_automation import TimeoutMonitor

    config = windows.config()
    window_element: WindowElement

    if timeout is None:
        timeout = config.timeout

    timeout_monitor = TimeoutMonitor(time.time() + timeout)

    ret: List[WindowElement] = []
    from robocorp.windows._find_ui_automation import find_ui_automation_wrappers

    for loc in _iter_window_locators(locator):
        # Use no timeout here (just a single search).
        for element in find_ui_automation_wrappers(
            loc,
            search_depth,
            root_element=root_element,
            timeout=0,
            search_strategy=search_strategy,
            wait_for_element=False,
        ):
            window_element = WindowElement(element)
            ret.append(window_element)

    while wait_for_window and not ret and not timeout_monitor.timed_out():
        # We have to keep on searching until the timeout is reached.
        # Note that we don't wait for an element (so, we should not wait
        # inside that function) but we still pass the timeout_monitor so that
        # it may return early if the timeout was reached.
        time.sleep(1 / 15.0)
        for loc in _iter_window_locators(locator):
            for element in find_ui_automation_wrappers(
                loc,
                search_depth,
                root_element=root_element,
                search_strategy=search_strategy,
                wait_for_element=False,
                timeout_monitor=timeout_monitor,
            ):
                window_element = WindowElement(element)
                ret.append(window_element)

    if wait_for_window and not ret:
        # No matches.
        _raise_window_not_found(locator, timeout, root_element)

    return ret
