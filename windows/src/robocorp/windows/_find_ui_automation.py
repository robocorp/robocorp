import re
import time
from dataclasses import dataclass
from re import Pattern
from typing import Dict, Iterator, List, Literal, Optional, Protocol, Set, Tuple, Union

from ._com_error import COMError
from ._config import IS_WINDOWS
from ._errors import ElementNotFound
from ._iter_tree import ControlTreeNode
from ._match_ast import OrSearchParams, SearchParams
from ._match_common import SearchType
from ._ui_automation_wrapper import _UIAutomationControlWrapper

if IS_WINDOWS:
    from ._vendored.uiautomation import Control
else:

    class Control:  # type:ignore
        pass


from .protocols import Locator


@dataclass
class LocatorStrAndOrSearchParams:
    locator: Locator
    or_search_params: Tuple[OrSearchParams, ...]

    def __str__(self):
        return self.locator

    def __repr__(self):
        return repr(self.locator)


def _window_or_none(
    window: "_UIAutomationControlWrapper",
) -> Optional["_UIAutomationControlWrapper"]:
    if window and window.item:
        try:
            window.item.BoundingRectangle
        except COMError:
            # Failure to get the bounding rectangle proves that the window doesn't
            #  exist anymore.
            return None

        return window

    return None


def _get_desktop_control() -> "Control":
    from ._vendored import uiautomation as auto

    root_control = auto.GetRootControl()
    assert root_control is not None, "Did not expect RootControl to be None."
    return root_control


def get_desktop_element() -> _UIAutomationControlWrapper:
    from ._ui_automation_wrapper import LocationInfo

    desktop_control = _get_desktop_control()
    location_info = LocationInfo("desktop", None, None, None)
    return _UIAutomationControlWrapper(desktop_control, location_info)


class ICompareFunc(Protocol):
    @classmethod
    def __call__(cls, el: ControlTreeNode["Control"], search_value) -> bool:
        pass


def _cmp_subname(el: ControlTreeNode["Control"], search_value) -> bool:
    if not isinstance(search_value, str):
        return False
    return search_value in el.control.Name


def _cmp_regex(el: ControlTreeNode["Control"], search_value) -> bool:
    return bool(re.match(search_value, el.control.Name))


def _cmp_depth(el: ControlTreeNode["Control"], search_value) -> bool:
    return el.depth == search_value


def _cmp_executable(el: ControlTreeNode["Control"], search_value) -> bool:
    executable: Optional[str] = None
    try:
        from psutil import Process

        proc = Process(el.control.ProcessId)
        executable = proc.exe()
    except Exception:
        return False

    executable = executable.replace("\\", "/")
    search_value = search_value.replace("\\", "/").lower()
    return executable.lower().endswith(search_value)


_match_dispatch: Dict[Union[str, Pattern[str]], Union[str, ICompareFunc]] = {
    # Same thing
    "automationid": "AutomationId",
    "id": "AutomationId",
    # Same thing
    "control": "ControlTypeName",
    "type": "ControlTypeName",
    # All match name in different ways
    "name": "Name",
    "subname": _cmp_subname,
    "regex": _cmp_regex,
    # Unique
    "class": "ClassName",
    "handle": "NativeWindowHandle",
    "executable": _cmp_executable,
    # "desktop": -- handled directly as this is the root object.
    "depth": _cmp_depth,
    # "index": -- this is a property of the hierarchy
    # "path": -- this is a property of the hierarchy
    # "offset": "offset", -- not supported
}


def _matches(search_params: SearchType, tree_node: ControlTreeNode["Control"]):
    if not search_params:
        return False

    try:
        for search_key, search_val in search_params.items():
            comp_func_or_attr = _match_dispatch[search_key]
            if isinstance(comp_func_or_attr, str):
                if getattr(tree_node.control, comp_func_or_attr) != search_val:
                    return False
            elif not comp_func_or_attr(tree_node, search_val):
                return False
    except COMError:
        return False

    return True


def _get_control_from_path(
    search_params: SearchType, root_control: "Control"
) -> "Control":
    # Follow a path in the tree of controls until reaching the final target.
    path: List[int] = search_params["path"]
    current = root_control

    for index, position in enumerate(path):
        children = current.GetChildren()
        if position > len(children):
            partial_path = "|".join(str(pos) for pos in path[:index])

            raise ElementNotFound(
                f"Unable to retrieve child on position {position!r} under a parent"
                f" with partial path {partial_path!r}"
            )

        current = children[position - 1]

    return current


def _resolve_root(
    root_element: Optional[_UIAutomationControlWrapper],
) -> _UIAutomationControlWrapper:
    if root_element is None:
        return get_desktop_element()

    root = _window_or_none(root_element)
    if root is None:
        raise RuntimeError("`root_element` provided is no longer valid.")
    return root


# def _load_by_alias(self, criteria: str) -> str:
#     try:
#         from RPA.core.locators import LocatorsDatabase, WindowsLocator
#
#         locator = LocatorsDatabase.load_by_name(criteria, self._locators_path)
#         if isinstance(locator, WindowsLocator):
#             return locator.value
#     except ValueError:
#         pass
#
#     return criteria


def _find_ui_automation_wrappers(
    locator: Optional[LocatorStrAndOrSearchParams] = None,
    search_depth: int = 8,
    root_element: Optional[_UIAutomationControlWrapper] = None,
    search_strategy: Literal["siblings", "all", "single"] = "single",
    timeout_monitor: Optional["TimeoutMonitor"] = None,
) -> Iterator[_UIAutomationControlWrapper]:
    from ._ui_automation_wrapper import build_from_locator_and_control_tree_node

    if not locator:
        yield _resolve_root(root_element)
        return

    root_control = _resolve_root(root_element).item

    # The timeout approach is the following: until we hit at least one object
    # with the given structure, we'll keep on searching, but at least one full
    # search should be done until the timeout is hit.

    search_params_by_level = locator.or_search_params
    match_level: OrSearchParams

    for i, match_level in enumerate(search_params_by_level):
        if timeout_monitor and timeout_monitor.timed_out():
            return

        is_last = i == len(search_params_by_level) - 1
        # Prepare control search parameters.

        if is_last:
            if search_strategy == "all":
                for control_tree_node, _found_params in _search_step(
                    locator.locator,
                    root_control,
                    match_level,
                    search_depth,
                    timeout_monitor,
                ):
                    location_info = build_from_locator_and_control_tree_node(
                        locator.locator,
                        control_tree_node,
                    )

                    yield _UIAutomationControlWrapper(
                        control_tree_node.control, location_info
                    )
                return

        try:
            root_control_tree_node, found_params = next(
                _search_step(
                    locator.locator,
                    root_control,
                    match_level,
                    search_depth,
                    timeout_monitor,
                )
            )
            root_control = root_control_tree_node.control
        except StopIteration:
            return
        else:
            if is_last:
                location_info = build_from_locator_and_control_tree_node(
                    locator.locator,
                    root_control_tree_node,
                )

                yield _UIAutomationControlWrapper(root_control, location_info)

                found_params.pop("desktop", None)
                found_params.pop("path", None)
                if not found_params:
                    # Can't keep on searching for matches in this case
                    return

                if search_strategy == "siblings":
                    # When searching siblings, we only search for the depth
                    # of the first found element anyways.
                    found_params.pop("depth", None)
                    yield from _search_siblings(
                        root_control_tree_node,
                        root_control,
                        found_params,
                        locator.locator,
                    )
                    return
                assert search_strategy is None
                # Don't keep on searching as the strategy is for a single match.
                return


def _search_step(
    locator: str,
    root_control,
    or_search_params: OrSearchParams,
    search_depth,
    timeout_monitor: Optional["TimeoutMonitor"],
) -> Iterator[Tuple[ControlTreeNode["Control"], SearchType]]:
    from ._control_element import ControlElement
    from ._ui_automation_wrapper import build_from_locator_and_control_tree_node

    errors: List[str] = []

    keep_searching: List[SearchType] = []
    for s in or_search_params.parts:
        # First check the heuristics to match it directly.
        try:
            assert isinstance(s, SearchParams)
            search_params = s.search_params

            # Obtain an element with the search parameters.
            if "desktop" in search_params:
                control = _get_desktop_control()
                yield (
                    ControlTreeNode(
                        control,
                        depth=0,
                        child_pos=0,
                        path="",
                    ),
                    search_params,
                )
                return

            if "path" in search_params:
                path_param = search_params["path"]
                control = _get_control_from_path(search_params, root_control)

                path_str = "|".join(str(x) for x in path_param)
                node = ControlTreeNode(
                    control,
                    depth=len(path_param),
                    child_pos=path_param[-1],
                    path=path_str,
                )
                remaining_params = search_params.copy()
                remaining_params.pop("path")
                if not remaining_params or _matches(remaining_params, node):
                    yield (node, search_params)
                    return

                location_info = build_from_locator_and_control_tree_node(locator, node)
                # Convert to have the proper __str__ representation to show to the user.
                as_el = ControlElement(
                    _UIAutomationControlWrapper(control, location_info)
                )
                raise ElementNotFound(
                    f"Found element: '{str(as_el).strip()}' in path, but other "
                    f"search parameters ({remaining_params}) did not match."
                )

            # Add it here if it didn't have 'desktop' nor 'path'.
            keep_searching.append(search_params)
        except ElementNotFound as e:
            errors.append(str(e))

    if not keep_searching:
        if errors:
            raise ElementNotFound("\n\n".join(errors))
        raise ElementNotFound(f"Unable to find locator: {locator!r}")

    # It didn't find it yet, fallback to the tree search.
    found_depths: List[int] = []
    for search_params in keep_searching:
        if "depth" in search_params:
            depth = int(search_params["depth"])
            found_depths.append(depth)
            search_depth = max(search_depth, depth)

    only_depths: Optional[Set[int]] = None
    if len(found_depths) == len(keep_searching):
        # Ok, we can use it if it's the same for all (but otherwise, we need
        # iterate all as at least one of the conditions doesn't have a depth).
        only_depths = set(found_depths)
        search_depth = max(only_depths)  # We can restrict the max to it.

    from ._iter_tree import iter_tree

    found = False
    for el in iter_tree(root_control, max_depth=search_depth, only_depths=only_depths):
        if not found:
            # If we found one item, we cannot time-out anymore.
            if timeout_monitor and timeout_monitor.timed_out():
                return
        for search_params in keep_searching:
            if _matches(search_params, el):
                found = True
                yield (el, search_params)


def _search_siblings(
    root_control_tree_node: ControlTreeNode,
    root_control: "Control",
    search_params: SearchType,
    locator: str,
) -> Iterator[_UIAutomationControlWrapper]:
    from ._ui_automation_wrapper import LocationInfo

    depth = root_control_tree_node.depth
    child_pos = root_control_tree_node.child_pos
    parent_path = "|".join(root_control_tree_node.path.split("|")[:-1])

    while True:
        next_control = root_control.GetNextSiblingControl()
        if not next_control:
            break

        child_pos += 1

        if _matches(search_params, ControlTreeNode(next_control, 0, 0, "")):
            path = f"{parent_path}|{child_pos}"

            location_info = LocationInfo(locator, depth, child_pos, path)
            element = _UIAutomationControlWrapper(next_control, location_info)
            yield element
        root_control = next_control


def find_ui_automation_wrapper(
    locator: Optional[LocatorStrAndOrSearchParams] = None,
    search_depth: int = 8,
    root_element: Optional[_UIAutomationControlWrapper] = None,
    timeout: Optional[float] = None,
    wait_for_element: bool = True,
) -> _UIAutomationControlWrapper:
    if wait_for_element:
        from . import config

        if timeout is not None:
            use_timeout = timeout
        else:
            use_timeout = config().timeout
        timeout_at = time.monotonic() + use_timeout

    timeout_monitor = None
    while True:
        for wrapper in _find_ui_automation_wrappers(
            locator,
            search_depth,
            root_element,
            search_strategy="single",
            timeout_monitor=timeout_monitor,
        ):
            return wrapper

        if not wait_for_element:
            break
        else:
            if time.monotonic() > timeout_at:
                break
            else:
                time.sleep(0.05)
                # Assign the timeout monitor only after at least one full
                # search was done.
                timeout_monitor = TimeoutMonitor(timeout_at)

    raise ElementNotFound(f"Unable to find element with locator: {locator!r}.")


def find_ui_automation_wrappers(
    locator: Optional[LocatorStrAndOrSearchParams] = None,
    search_depth: int = 8,
    root_element: Optional[_UIAutomationControlWrapper] = None,
    timeout: Optional[float] = None,
    search_strategy: Literal["siblings", "all"] = "siblings",
    wait_for_element: bool = False,
    timeout_monitor: Optional["TimeoutMonitor"] = None,
) -> List[_UIAutomationControlWrapper]:
    """Get a list of elements matching the locator.

    By default, only the siblings (similar elements on the same level) are taken
    into account. In order to search globally, set `search_strategy="all"`, but be
    aware that this will take more time to process.

    Args:
        locator: Locator string.
        search_depth: How deep the element search will traverse. (default 8)
        root_element: Will be used as search root element object if provided.
        timeout: After how many seconds (float) to give up on search. Note
            that at least one full search up to the given depth will be done.
            Only used if `wait_for_element` is True.
        search_strategy:
            "siblings": only the siblings (similar elements on the same level)
                will be found
            "all": all the elements available (up to the search_depth) will be
                searched.
        wait_for_element: Defines whether the search should wait for some element
            to be found.
        timeout_monitor: If given, ignores the timeout parameter and uses the
            TimeoutMonitor passed instead (meaning that it may timeout even
            before a single full search is done). It's used even if wait_for_element
            is False.
    """
    if wait_for_element:
        from . import config

        if timeout is not None:
            use_timeout = timeout
        else:
            use_timeout = config().timeout
        timeout_at = time.monotonic() + use_timeout

    def _timed_out() -> bool:
        if timeout_monitor is not None:
            return timeout_monitor.timed_out()
        else:
            return time.monotonic() > timeout_at

    while True:
        # At least one search is always done (although it may time-out if
        # the timeout_monitor was passed).
        ret = list(
            _find_ui_automation_wrappers(
                locator,
                search_depth,
                root_element,
                search_strategy=search_strategy,
                timeout_monitor=timeout_monitor,
            )
        )
        if not wait_for_element or len(ret) > 0:
            return ret
        else:
            if _timed_out():
                return ret  # timed out, return even if the list is empty
            else:
                time.sleep(1 / 15.0)
                # Assign the timeout monitor only after at least one full
                # search was done.
                if timeout_monitor is None:
                    timeout_monitor = TimeoutMonitor(timeout_at)


class TimeoutMonitor:
    def __init__(self, timeout_at: float):
        self.timeout_at = timeout_at

    def timed_out(self):
        return time.monotonic() > self.timeout_at
