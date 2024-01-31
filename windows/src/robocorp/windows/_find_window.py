import logging
import time
from typing import List, Literal, Optional, Tuple, overload

from ._errors import ElementNotFound
from ._match_ast import OrSearchParams, SearchParams
from ._ui_automation_wrapper import _UIAutomationControlWrapper
from ._window_element import WindowElement
from .protocols import Locator

logger = logging.getLogger(__name__)


def restrict_to_window_locators(
    or_search_params: Tuple[OrSearchParams, ...],
) -> Tuple[OrSearchParams, ...]:
    last_part: OrSearchParams = or_search_params[-1]
    also_add_as_pane = []
    for search_params in last_part.parts:
        assert isinstance(search_params, SearchParams)

        # Ok, leave is is (the type is already defined)
        if search_params.search_params.get(
            "control", search_params.search_params.get("type")
        ):
            continue

        # Now, for each search param we have to add a new entry where we check
        # for both 'WindowControl' and 'PaneControl'
        also_add_as_pane.append(search_params.copy())
        search_params.search_params["type"] = "WindowControl"

    for param in also_add_as_pane:
        param.search_params["type"] = "PaneControl"
        last_part.parts.append(param)

    return or_search_params


@overload
def find_window(
    root_element: Optional[_UIAutomationControlWrapper],
    locator: Locator,
    search_depth: int = ...,
    timeout: Optional[float] = ...,
    wait_time: Optional[float] = ...,
    foreground: bool = ...,
    raise_error: Literal[True] = ...,
) -> WindowElement:
    ...


@overload
def find_window(
    root_element: Optional[_UIAutomationControlWrapper],
    locator: Locator,
    search_depth: int = ...,
    timeout: Optional[float] = ...,
    wait_time: Optional[float] = ...,
    foreground: bool = ...,
    raise_error: Literal[False] = ...,
) -> Optional[WindowElement]:
    ...


@overload
def find_window(
    root_element: Optional[_UIAutomationControlWrapper],
    locator: Locator,
    search_depth: int = ...,
    timeout: Optional[float] = ...,
    wait_time: Optional[float] = ...,
    foreground: bool = ...,
    raise_error: bool = ...,
) -> Optional[WindowElement]:
    ...


def find_window(
    root_element: Optional[_UIAutomationControlWrapper],
    locator: Locator,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None,
    foreground: bool = True,
    raise_error: bool = True,
) -> Optional[WindowElement]:
    from . import config as windows_config
    from ._find_ui_automation import (
        LocatorStrAndOrSearchParams,
        find_ui_automation_wrapper,
    )
    from ._match_ast import collect_search_params

    config = windows_config()
    or_search_params = collect_search_params(locator)
    restrict_to_window_locators(or_search_params)

    locator_and_or_search_params = LocatorStrAndOrSearchParams(
        locator, or_search_params
    )

    if timeout is None:
        timeout = config.timeout

    assert timeout is not None
    if wait_time is None:
        wait_time = config.wait_time

    try:
        element = find_ui_automation_wrapper(
            locator_and_or_search_params,
            search_depth,
            root_element=root_element,
            timeout=timeout,
        )
        window_element = WindowElement(element)
        if foreground:
            window_element.foreground_window()
        if wait_time:
            time.sleep(wait_time)
        return window_element
    except ElementNotFound as exc:
        # No matches.
        if raise_error:
            _raise_window_not_found(locator, timeout, root_element)
        else:
            logger.warning(exc)
        return None


def _raise_window_not_found(
    locator: Locator, timeout, root_element: Optional[_UIAutomationControlWrapper]
):
    from . import config as windows_config
    from ._match_ast import _build_locator_match

    config = windows_config()

    msg = (
        f"Could not locate window with locator: {locator!r} "
        f"(timeout: {timeout if timeout is not None else config.timeout})"
    )

    locator_match = _build_locator_match(locator)
    msg += f"\nLocator internal representation: {locator_match}"
    for warning in locator_match.warnings:
        msg += f"\nLocator warning: {warning}"

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
    from . import config as windows_config
    from ._find_ui_automation import (
        LocatorStrAndOrSearchParams,
        TimeoutMonitor,
        find_ui_automation_wrappers,
    )
    from ._match_ast import collect_search_params

    config = windows_config()
    window_element: WindowElement

    if timeout is None:
        timeout = config.timeout

    timeout_monitor = TimeoutMonitor(time.time() + timeout)

    ret: List[WindowElement] = []

    or_search_params = collect_search_params(locator)
    restrict_to_window_locators(or_search_params)

    locator_and_or_search_params = LocatorStrAndOrSearchParams(
        locator, or_search_params
    )

    # Use no timeout here (just a single search).
    for element in find_ui_automation_wrappers(
        locator_and_or_search_params,
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
        for element in find_ui_automation_wrappers(
            locator_and_or_search_params,
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
