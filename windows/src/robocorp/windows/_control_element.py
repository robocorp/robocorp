# ruff: noqa: E501
import inspect
import itertools
import logging
import re
import sys
import typing
from pathlib import Path
from typing import Callable, Iterator, List, Literal, Optional, Tuple, Union, overload

from ._com_error import COMError
from ._errors import ActionNotPossible, ElementNotFound
from ._find_ui_automation import LocatorStrAndOrSearchParams
from .protocols import Locator

if typing.TYPE_CHECKING:
    from PIL.Image import Image

    from ._iter_tree import ControlTreeNode
    from ._ui_automation_wrapper import _UIAutomationControlWrapper
    from ._vendored.uiautomation.uiautomation import (
        Control,
        LegacyIAccessiblePattern,
        ValuePattern,
    )


PatternType = Union["ValuePattern", "LegacyIAccessiblePattern"]

DEFAULT_SEND_KEYS_INTERVAL = 0.01


class _SentinelValidator:
    # Used to determine the validator function for `ControlElement.set_value` method.
    #  If a validator is not passed explicitly, then the `set_value_validator` function
    #  will be used as default.

    def __call__(self, *args, **kwargs):
        pass

    def __repr__(self):
        return "_SentinelValidator"

    def __str__(self):
        return "_SentinelValidator"


def set_value_validator(expected: str, actual: str) -> bool:
    """Checks the passed against the final set value and returns status."""
    return actual.strip() == expected.strip()  # due to EOLs inconsistency


def _wait_time() -> float:
    """
    Internal API to get the global wait time (usually used as default when
    one is not set in a given API).
    """
    from . import config

    return config().wait_time


def _simulate_move() -> bool:
    """
    Internal API to determine if the mouse movement should be simulated.
    """
    from . import config

    return config().simulate_mouse_movement


class ControlElement:
    """
    Class used to interact with a control.
    """

    logger = logging.getLogger(__name__)

    def __init__(self, wrapped: "_UIAutomationControlWrapper"):
        self._wrapped = wrapped
        self.location_info = self._wrapped.location_info

    @property
    def path(self) -> Optional[str]:
        """
        Provides the relative path in which this element was found

        Note: this is relative to the element which was used for the `find` or
        `find_window` and cannot be used as an absolute path to be used to find
        the control from the desktop.
        """
        return self.location_info.path

    def inspect(self) -> None:
        """
        Starts inspecting with this element as the root element upon which
        other elements will be found (i.e.: only elements under this element
        in the hierarchy will be inspected, other elements can only be inspected
        if the inspection root is changed).

        Example:

            ```python
            from robocorp import windows
            windows.find_window('Calculator').inspect()
            ```
        """
        from ._inspect import ElementInspector

        element_inspector = ElementInspector(self)
        element_inspector.inspect()

    def get_parent(self) -> Optional["ControlElement"]:
        """
        Returns:
            The parent element for this control.
        """
        parent = self._wrapped.get_parent()
        if parent is None:
            return None
        return ControlElement(parent)

    def is_same_as(self, other: "ControlElement") -> bool:
        """
        Args:
            other: The element to compare to.

        Returns:
            True if this elements points to the same element represented
            by the other control.
        """
        from ._vendored.uiautomation.uiautomation import ControlsAreSame

        return ControlsAreSame(self._wrapped.item, other._wrapped.item)

    def _find_ui_automation_wrapper(
        self,
        locator: Optional[LocatorStrAndOrSearchParams] = None,
        search_depth: int = 8,
        timeout: Optional[float] = None,
    ) -> "_UIAutomationControlWrapper":
        """
        Internal API to find the control to interact with given a locator.
        """
        from ._find_ui_automation import find_ui_automation_wrapper

        root = self._wrapped

        self.logger.info("Getting element with locator: %s", locator)
        if not locator:
            return root

        element = find_ui_automation_wrapper(
            locator, search_depth, timeout=timeout, root_element=root
        )
        self.logger.info("Returning element: %s", element)
        return element

    @property
    def ui_automation_control(self) -> "Control":
        """
        Provides the Control actually wrapped by this ControlElement.
        Can be used as an escape hatch if some functionality is not directly
        covered by this class (in general this API should only be used if
        a better API isn't directly available in the ControlElement).
        """
        return self._wrapped.item

    def is_disposed(self) -> bool:
        """
        Returns:
            True if the underlying control is already disposed and False
            otherwise.
        """
        try:
            self._wrapped.item.Name
        except COMError:
            return True
        else:
            return False

    @property
    def handle(self) -> int:
        """
        Returns:
            The internal native window handle from the control wrapped in this
            class.
        """
        return self._wrapped.handle

    def has_keyboard_focus(self) -> bool:
        """
        Returns:
            True if this control currently has keyboard focus.
        """
        return self._wrapped.item.HasKeyboardFocus

    @property
    def name(self) -> str:
        """
        Returns:
            The name of the underlying control wrapped in this class
            (matches the locator `name`).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned.
        """
        return self._wrapped.name

    @property
    def automation_id(self) -> str:
        """
        Returns:
            The automation id of the underlying control wrapped in this class
            (matches the locator `automationid` or `id`).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned.
        """
        return self._wrapped.automation_id

    @property
    def control_type(self) -> str:
        """
        Returns:
            The control type of the underlying control wrapped in this class
            (matches the locator `control` or `type`).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned.
        """
        return self._wrapped.control_type

    @property
    def class_name(self) -> str:
        """
        Returns:
            The class name of the underlying control wrapped in this class
            (matches the locator `class`).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned.
        """
        return self._wrapped.class_name

    @property
    def left(self) -> int:
        """
        Returns:
            The left bound of the control (-1 if invalid).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned. The method `update_geometry()` may
            be used to get the new bounds of the control.
        """
        return self._wrapped.left

    @property
    def right(self) -> int:
        """
        Returns:
            The right bound of the control (-1 if invalid).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned. The method `update_geometry()` may
            be used to get the new bounds of the control.
        """
        return self._wrapped.right

    @property
    def top(self) -> int:
        """
        Returns:
            The top bound of the control (-1 if invalid).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned. The method `update_geometry()` may
            be used to get the new bounds of the control.
        """
        return self._wrapped.top

    @property
    def bottom(self) -> int:
        """
        Returns:
            The bottom bound of the control (-1 if invalid).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned. The method `update_geometry()` may
            be used to get the new bounds of the control.
        """
        return self._wrapped.bottom

    @property
    def width(self) -> int:
        """
        Returns:
            The width of the control (-1 if invalid).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned. The method `update_geometry()` may
            be used to get the new bounds of the control.
        """
        return self._wrapped.width

    @property
    def height(self) -> int:
        """
        Returns:
            The height of the control (-1 if invalid).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned. The method `update_geometry()` may
            be used to get the new bounds of the control.
        """
        return self._wrapped.height

    @property
    def rectangle(self) -> Tuple[int, int, int, int]:
        """
        Returns:
            A tuple with (left, top, right, bottom) -- (all -1 if invalid).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned. The method `update_geometry()` may
            be used to get the new bounds of the control.
        """
        return (self.left, self.top, self.right, self.bottom)

    @property
    def xcenter(self) -> int:
        """
        Returns:
            The x position of the center of the control (-1 if invalid).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned. The method `update_geometry()` may
            be used to get the new bounds of the control.
        """
        return self._wrapped.xcenter

    @property
    def ycenter(self) -> int:
        """
        Returns:
            The y position of the center of the control (-1 if invalid).

        Note:
            This value is cached when the element is created and even if the
            related value of the underlying control changes the initial value
            found will still be returned. The method `update_geometry()` may
            be used to get the new bounds of the control.
        """
        return self._wrapped.ycenter

    def has_valid_geometry(self) -> bool:
        """
        Returns:
            True if the geometry of this element is valid and False otherwise.

        Note:
            This value is based on cached coordinates. Call `update_geometry()`
            to check it based on the current bounds of the control.
        """
        if self.width == 0 or self.height == 0:
            return False

        left, top, right, bottom = self.rectangle
        return not bool(left == -1 and top == -1 and right == -1 and bottom == -1)

    def update_geometry(self) -> None:
        """
        This method may be called to update the cached coordinates of the
        control bounds.
        """
        self._wrapped.update_geometry()

    def __str__(self) -> str:
        # Print what can be used in the locator.
        handle = self.handle

        def fmt(s):
            s = str(s)
            if not s:
                return '""'

            if " " in s:
                s = f'"{s}"'
            return s

        # These are cached, so, no need for try..except here.
        location_info = self.location_info

        lst = []

        if location_info.query_locator:
            lst.append(f"locator:{location_info.query_locator}")

        if location_info.depth:
            lst.append(f"depth:{location_info.depth}")

        if location_info.child_pos:
            lst.append(f"index:{location_info.child_pos}")

        if location_info.path:
            lst.append(f"path:{location_info.path}")

        info = (
            f"control:{fmt(self.control_type)} "
            f"class:{fmt(self.class_name)} "
            f"name:{fmt(self.name)} "
            f"id:{fmt(self.automation_id)} "
            f"handle:0x{handle:X}({handle})"
        )
        if lst:
            s = " ".join(lst)

            info = f"{info} Search info({s})"
        return info

    def __repr__(self):
        return f"""{self.__class__.__name__}({self.__str__()})"""

    def _raise_or_warn_control_not_found(
        self,
        locator: Locator,
        search_depth: int,
        timeout: Optional[float],
        raise_error: bool,  # to raise or not
        exception: Exception,  # previous original raised exception
    ):
        from . import config as windows_config

        config = windows_config()
        if not config.verbose_errors:
            # Verbose errors were disabled, so no fancy messages with suggestions will
            #  be applied.
            if raise_error:
                # Just re-raise the same error if raising is ON.
                raise exception
            else:
                # Or log instead without raising.
                self.logger.warning(exception)
                return

        # Verbose error message with suggestions.
        msg = (
            f"Could not locate control with locator: {locator!r} "
            f"(timeout: {timeout if timeout is not None else config.timeout})"
        )
        if not raise_error:
            # Verbosity not needed anymore when raising was disabled.
            self.logger.warning(msg)
            return

        child_elements_msg = ["\nChild Elements Found:"]
        for child in self._iter_children_nodes(max_depth=search_depth):
            child_elements_msg.append(str(child))
        msg += "\n".join(child_elements_msg)
        raise ElementNotFound(msg) from exception

    @overload
    def find(
        self,
        locator: Locator,
        search_depth: int = ...,
        timeout: Optional[float] = ...,
        raise_error: Literal[True] = ...,
    ) -> "ControlElement":
        ...

    @overload
    def find(
        self,
        locator: Locator,
        search_depth: int = ...,
        timeout: Optional[float] = ...,
        raise_error: Literal[False] = ...,
    ) -> Optional["ControlElement"]:
        ...

    @overload
    def find(
        self,
        locator: Locator,
        search_depth: int = ...,
        timeout: Optional[float] = ...,
        raise_error: bool = ...,
    ) -> Optional["ControlElement"]:
        ...

    def find(
        self,
        locator: Locator,
        search_depth: int = 8,
        timeout: Optional[float] = None,
        raise_error: bool = True,
    ) -> Optional["ControlElement"]:
        """
        This method may be used to find a control in the descendants of this
        control.

        The first matching element is returned.

        Args:
            locator: The locator to be used to search a child control.

            search_depth: Up to which depth the hierarchy should be searched.

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.

            raise_error: Do not raise and return `None` when this is set to `True` and such
                a window isn't found.

        Raises:
            `ElementNotFound` if an element with the given locator could not be
            found.
        """
        if not locator:
            return self
        try:
            return ControlElement(
                self._find_ui_automation_wrapper(
                    self._convert_locator_to_locator_and_or_search_params(locator),
                    search_depth,
                    timeout=timeout,
                )
            )
        except ElementNotFound as exc:
            self._raise_or_warn_control_not_found(
                locator, search_depth, timeout, raise_error, exception=exc
            )
            return None

    def find_many(
        self,
        locator: Locator,
        search_depth: int = 8,
        timeout: Optional[float] = None,
        search_strategy: Literal["siblings", "all"] = "siblings",
        wait_for_element=False,
    ) -> List["ControlElement"]:
        """
        This method may be used to find multiple descendants of the current
        element matching the given locator.

        Args:
            locator: The locator that should be used to find elements.

            search_depth: Up to which depth the tree will be traversed.

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `wait_for_element` is True.

            search_strategy: The search strategy to be used to find elements.
                `siblings` means that after the first element is found, the tree
                    traversal should be stopped and only sibling elements will be
                    searched.
                `all` means that all the elements up to the given search depth
                    will be searched.

            wait_for_element: Defines whether the search should keep on searching
                until an element with the given locator is found (note that if True
                and no element was found an ElementNotFound is raised).

        Note:
            Keep in mind that by default the search strategy is for searching
            `siblings` of the initial element found (so, by default, after the first
            element is found a tree traversal is not done and only sibling elements
            from the initial element are found). Use the `all` search strategy to
            search for all elements.
        """
        from ._find_ui_automation import find_ui_automation_wrappers

        return [
            ControlElement(x)
            for x in find_ui_automation_wrappers(
                self._convert_locator_to_locator_and_or_search_params(locator),
                search_depth,
                root_element=self._wrapped,
                timeout=timeout,
                search_strategy=search_strategy,
                wait_for_element=wait_for_element,
            )
        ]

    def _convert_locator_to_locator_and_or_search_params(
        self, locator: Optional[Locator]
    ) -> Optional[LocatorStrAndOrSearchParams]:
        if locator is None:
            return None
        from ._match_ast import collect_search_params

        locator_and_or_search_params = LocatorStrAndOrSearchParams(
            locator, collect_search_params(locator)
        )
        return locator_and_or_search_params

    def _iter_children_nodes(
        self, *, max_depth: int = 8
    ) -> Iterator["ControlTreeNode[ControlElement]"]:
        """
        Internal API to provide structure with a `ControlTreeNode` for printing.
        Not part of the public API (should not be used by client code).
        """

        from ._iter_tree import ControlTreeNode, iter_tree
        from ._ui_automation_wrapper import LocationInfo, _UIAutomationControlWrapper

        for el in iter_tree(self._wrapped.item, max_depth):
            location_info = LocationInfo(None, el.depth, el.child_pos, el.path)
            wrapper = _UIAutomationControlWrapper(el.control, location_info)
            if wrapper.is_disposed():
                continue

            yield ControlTreeNode(
                ControlElement(wrapper), el.depth, el.child_pos, el.path
            )

    def iter_children(self, *, max_depth: int = 8) -> Iterator["ControlElement"]:
        """
        Iterates over all of the children of this element up to the max_depth
        provided.

        Args:
            max_depth: the maximum depth which should be iterated to.

        Returns:
            An iterator of `ControlElement` which provides the descendants of
            this element.

        Note:
            Iteration over too many items can be slow. Try to keep the
            max depth up to a minimum to avoid slow iterations.
        """

        from ._iter_tree import iter_tree
        from ._ui_automation_wrapper import LocationInfo, _UIAutomationControlWrapper

        for el in iter_tree(self._wrapped.item, max_depth):
            location_info = LocationInfo(None, el.depth, el.child_pos, el.path)
            wrapper = _UIAutomationControlWrapper(el.control, location_info)
            if wrapper.is_disposed():
                continue

            yield ControlElement(wrapper)

    def print_tree(
        self, stream=None, show_properties: bool = False, max_depth: int = 8
    ) -> None:
        """
        Print a tree of control elements.

        A Windows application structure can contain multilevel element structure.
        Understanding this structure is crucial for creating locators. (based on
        controls' details and their parent-child relationship)

        This method can be used to output logs of application's element structure.

        The printed element attributes correspond to the values that may be used
        to create a locator to find the actual wanted element.

        Args:
            stream: The stream to which the text should be printed (if not given,
                sys.stdout is used).

            show_properties: Whether the properties of each element should
                be printed (off by default as it can be considerably slower
                and makes the output very verbose).

            max_depth: Up to which depth the tree should be printed.

        Example:

            Print the top-level window elements:

            ```python
            from robocorp import windows
            windows.desktop().print_tree()
            ```

        Example:

            Print the tree starting at some other element:

            ```python
            from robocorp import windows
            windows.find("Calculator > path:2|3").print_tree()
            ```
        """
        from ._iter_tree import ControlTreeNode

        if stream is None:
            stream = sys.stderr

        # Show the root.
        root = ControlTreeNode(self, 0, 0, "")
        iter_in = itertools.chain(
            (root,), self._iter_children_nodes(max_depth=max_depth)
        )

        if not show_properties:
            for child in iter_in:
                print(child, file=stream)
        else:
            for child in iter_in:
                print(child, file=stream)

                space = " " * (child.depth * 4 + 2)
                control = child.control
                print(f"{space}Properties:", file=stream)
                try:
                    v = control.get_value()
                    print(f"  {space}get_value() = {v!r}", file=stream)
                except ActionNotPossible:
                    pass
                try:
                    v = control.get_text()
                    print(f"  {space}get_text() = {v!r}", file=stream)
                except ActionNotPossible:
                    pass

                ui_automation_control = control.ui_automation_control
                # Skip attributes which don't seem relevant.
                skip_attributes = {
                    "ValidKeys",
                    "CreateControlFromControl",
                    "CreateControlFromElement",
                    "searchDepth",
                    "searchFromControl",
                    "searchInterval",
                    "searchProperties",
                }
                for attr in dir(ui_automation_control):
                    if attr.startswith("_") or attr in skip_attributes:
                        continue
                    try:
                        try:
                            v = getattr(ui_automation_control, attr)
                        except AttributeError:
                            pass
                        else:
                            if v:
                                if inspect.ismethod(v):
                                    if not attr.startswith(
                                        "Is"
                                    ) and not attr.startswith("Has"):
                                        continue

                                    v = v()
                                    print(
                                        (
                                            f"  {space}ui_automation_control."
                                            f"{attr}() = {v}"
                                        ),
                                        file=stream,
                                    )
                                else:
                                    print(
                                        f"  {space}ui_automation_control.{attr} = {v}",
                                        file=stream,
                                    )
                    except ActionNotPossible:
                        pass

    def mouse_hover(self) -> None:
        """
        Moves the mouse to the center of this element to simulate a mouse hovering.
        """
        from ._vendored.uiautomation.uiautomation import SetCursorPos

        self.update_geometry()
        if not self.has_valid_geometry():
            raise ActionNotPossible(
                f"Cannot hover because the element ({self}) does not have a valid geometry."
            )
        SetCursorPos(self.xcenter, self.ycenter)

    def click(
        self,
        locator: Optional[Locator] = None,
        *,
        search_depth: int = 8,
        timeout: Optional[float] = None,
        wait_time: Optional[float] = None,
    ) -> "ControlElement":
        """
        Clicks an element using the mouse.

        Args:
            locator: If given the child element which matches this locator will
                be clicked.
            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).
            wait_time: The time to wait after clicking the element. If not passed the
                default value found in the config is used.
            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is passed.

        Example:

            Click using a locator:

            ```python
            from robocorp import windows
            windows.find_window('Calculator').click('id:button1')
            ```

            Click customizing wait time after the click:

            ```python
            from robocorp import windows
            calculator_window = windows.find_window('Calculator')
            calculator_window.find('name:SendButton').click(wait_time=5.0)
            ```

            Make an existing window foreground so that it can be clicked:

            ```python
            window.foreground_window()
            window.click('name:SendButton', wait_time=5.0)
            ```

        Returns:
            The clicked element.

        Note:
            The element clicked must be visible in the screen, if it's hidden
            by some other window or control the click will not work.

        Raises:
            ActionNotPossible: if element does not allow the Click action.
        """
        return self._mouse_click(locator, search_depth, "Click", wait_time, timeout)

    def double_click(
        self,
        locator: Optional[Locator] = None,
        *,
        search_depth: int = 8,
        timeout: Optional[float] = None,
        wait_time: Optional[float] = None,
    ) -> "ControlElement":
        """
        Double-clicks an element using the mouse.

        Args:
            locator: If given the child element which matches this locator will
                be double-clicked.

            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is passed.

            wait_time: The time to wait after double-clicking the element. If not
                passed the default value found in the config is used.

        Example:

            Double-click using a locator:

            ```python
            from robocorp import windows
            windows.find_window('Calculator').double_click('id:button1')
            ```

            Click customizing wait time after the double-click:

            ```python
            from robocorp import windows
            calculator_window = windows.find_window('Calculator')
            calculator_window.find('name:SendButton').double_click(wait_time=5.0)
            ```

            Make an existing window foreground so that it can be double-clicked:

            ```python
            window.foreground_window()
            window.double_click('name:SendButton', wait_time=5.0)
            ```

        Returns:
            The clicked element.

        Note:
            The element clicked must be visible in the screen, if it's hidden
            by some other window or control the double-click will not work.

        Raises:
            ActionNotPossible: if element does not allow the double-click action.
        """

        return self._mouse_click(
            locator, search_depth, "DoubleClick", wait_time, timeout
        )

    def right_click(
        self,
        locator: Optional[Locator] = None,
        *,
        search_depth: int = 8,
        timeout: Optional[float] = None,
        wait_time: Optional[float] = None,
    ) -> "ControlElement":
        """
        Right-clicks an element using the mouse.

        Args:
            locator: If given the child element which matches this locator will
                be right-clicked.
            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).
            wait_time: The time to wait after right-clicking the element. If not
                passed the default value found in the config is used.
            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is passed.

        Example:

            Right-click using a locator:

            ```python
            from robocorp import windows
            windows.find_window('Calculator').right_click('id:button1')
            ```

            Click customizing wait time after the right-click:

            ```python
            from robocorp import windows
            calculator_window = windows.find_window('Calculator')
            calculator_window.find('name:SendButton').right_click(wait_time=5.0)
            ```

            Make an existing window foreground so that it can be right-clicked:

            ```python
            window.foreground_window()
            window.right_click('name:SendButton', wait_time=5.0)
            ```

        Returns:
            The clicked element.

        Note:
            The element clicked must be visible in the screen, if it's hidden
            by some other window or control the right-click will not work.

        Raises:
            ActionNotPossible: if element does not allow the right-click action.
        """
        return self._mouse_click(
            locator, search_depth, "RightClick", wait_time, timeout
        )

    def middle_click(
        self,
        locator: Optional[Locator] = None,
        *,
        search_depth: int = 8,
        timeout: Optional[float] = None,
        wait_time: Optional[float] = None,
    ) -> "ControlElement":
        """
        Middle-clicks an element using the mouse.

        Args:
            locator: If given the child element which matches this locator will
                be middle-clicked.

            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is passed.

            wait_time: The time to wait after middle-clicking the element. If not
                passed the default value found in the config is used.

        Example:

            Middle-click using a locator:

            ```python
            from robocorp import windows
            windows.find_window('Calculator').middle_click('id:button1')
            ```

            Click customizing wait time after the middle-click:

            ```python
            from robocorp import windows
            calculator_window = windows.find_window('Calculator')
            calculator_window.find('name:SendButton').middle_click(wait_time=5.0)
            ```

            Make an existing window foreground so that it can be middle-clicked:

            ```python
            window.foreground_window()
            window.middle_click('name:SendButton', wait_time=5.0)
            ```

        Returns:
            The clicked element.

        Note:
            The element clicked must be visible in the screen, if it's hidden
            by some other window or control the middle-click will not work.

        Raises:
            ActionNotPossible: if element does not allow the middle-click action.
        """
        return self._mouse_click(
            locator, search_depth, "MiddleClick", wait_time, timeout
        )

    def _mouse_click(
        self,
        locator: Optional[Locator],
        search_depth: int,
        click_type: str,
        wait_time: Optional[float],
        timeout: Optional[float],
    ) -> "ControlElement":
        click_wait_time: float = wait_time if wait_time is not None else _wait_time()
        if not locator:
            element = self
        else:
            element = self.find(locator, search_depth, timeout=timeout)
        self._click_element(element, click_type, click_wait_time)
        return element

    def _click_element(
        self,
        element: "ControlElement",
        click_type: str,
        click_wait_time: float,
    ):
        control = element.ui_automation_control
        click_function = getattr(control, click_type, None)
        if not click_function:
            raise ActionNotPossible(
                f"Element {element!r} does not have the {click_type!r} attribute"
            )
        # Get a new fresh bounding box each time, since the element might have been
        #  moved from its initial spot.
        self.update_geometry()
        if not self.has_valid_geometry():
            if self.is_disposed():
                raise ActionNotPossible(
                    f"The element: {element!r} is already disposed. "
                    "Please do a new search from the parent/root to get a new valid handle."
                )

            raise ActionNotPossible(
                (
                    f"Element {element!r} is not visible for clicking. Ensure the root "
                    "window is the foreground window. If it is, consider doing a new "
                    "search for this element as the current reference may no longer be valid."
                )
            )

        log_message = f"{click_type}-ing element"

        self.logger.debug(log_message)
        click_function(
            # x=offset_x,
            # y=offset_y,
            simulateMove=_simulate_move(),
            waitTime=click_wait_time,
        )

    def select(
        self,
        value: str,
        *,
        locator: Optional[Locator] = None,
        search_depth: int = 8,
        timeout: Optional[float] = None,
    ) -> "ControlElement":
        """
        Select a value on the passed element if such action is supported.

        Args:
            value: value to select on element.

            locator: If given the child element which matches this locator will
                be used for the selection.

            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is passed.

        Returns:
            The element used in the selection.

        Raises:
            ActionNotPossible if the element does not allow the `Select` action.

        Note:
            This is usually used with combo box elements.

        Example:

            ```python
            element.select("22", locator="id:FontSizeComboBox")
            ```
        """
        if locator:
            element = self.find(locator, search_depth, timeout=timeout)
        else:
            element = self

        control = element.ui_automation_control
        if hasattr(control, "Select"):
            # NOTE(cmin764): This is not supposed to work on `*Pattern` or `TextRange`
            #  objects. (works with `Control`s and its derived flavors only, like a
            #  combobox)
            control.Select(value, simulateMove=_simulate_move(), waitTime=_wait_time())
        else:
            raise ActionNotPossible(
                f"Element {element!r} does not support selection (try with"
                " `Set Value` instead)"
            )
        return element

    def send_keys(
        self,
        keys: Optional[str] = None,
        interval: float = DEFAULT_SEND_KEYS_INTERVAL,
        send_enter: bool = False,
        *,
        locator: Optional[Locator] = None,
        search_depth: int = 8,
        timeout: Optional[float] = None,
        wait_time: Optional[float] = None,
    ) -> "ControlElement":
        """
        Sends the given keys to the element (simulates typing keys on the keyboard).

        Args:
            keys:
                The keys to be sent.
                Special keys may be sent as {Ctrl}{Alt}{Delete}, etc.

                Some examples of valid key combinations are shown below:

                ```python
                '{Ctrl}a{Delete}{Ctrl}v{Ctrl}s{Ctrl}{Shift}s{Win}e{PageDown}'  # press Ctrl+a, Delete, Ctrl+v, Ctrl+s, Ctrl+Shift+s, Win+e, PageDown
                '{Ctrl}(AB)({Shift}(123))'  # press Ctrl+A+B, type '(', press Shift+1+2+3, type ')', if '()' follows a hold key, hold key won't release util ')'
                '{Ctrl}{a 3}'  # press Ctrl+a at the same time, release Ctrl+a, then type 'a' 2 times
                '{a 3}{B 5}'  # type 'a' 3 times, type 'B' 5 times
                '{{}Hello{}}abc {a}{b}{c} test{} 3}{!}{a} (){(}{)}'  # type: '{Hello}abc abc test}}}!a ()()'
                '0123456789{Enter}'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ{Enter}'
                'abcdefghijklmnopqrstuvwxyz{Enter}'
                '`~!@#$%^&*()-_=+{Enter}'
                '[]{{}{}}\\|;:\'\",<.>/?{Enter}'
                ```


            interval: Time between each sent key. (defaults to 0.01 seconds)

            send_enter: If `True` then the {Enter} key is pressed at the end of the sent keys.

            locator: If given the child element which matches this locator will
                be used to send the keys.

            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is passed.

            wait_time: The time to wait after sending the keys to the element. If not passed the
                default value found in the config is used.

        Returns:
            The element to which the keys were sent.

        Example:
            ```python
            from robocorp import windows

            windows.desktop().send_keys('{Ctrl}{F4}')
            windows.find_window('Calculator').send_keys('96+4=', send_enter=True)
            ```

        Raises:
            ActionNotPossible: if the element does not allow the SendKeys action.
        """
        if not locator:
            element = self
        else:
            element = self.find(locator, search_depth, timeout=timeout)
        self._send_keys_to_element(
            element.ui_automation_control,
            keys or "",
            interval,
            wait_time,
            send_enter,
        )
        return element

    @classmethod
    def _send_keys_to_element(
        cls,
        control: "Control",
        keys: str,
        interval: float = DEFAULT_SEND_KEYS_INTERVAL,
        wait_time: Optional[float] = None,
        send_enter: bool = False,
    ):
        if hasattr(control, "SendKeys"):
            if wait_time is None:
                wait_time = _wait_time()
            cls.logger.info("Sending keys %r to control: %s", keys, control)
            if keys:
                control.SendKeys(text=keys, interval=interval, waitTime=wait_time)
            if send_enter:
                control.SendKeys(text="{Enter}", interval=interval, waitTime=wait_time)
        else:
            raise ActionNotPossible("Element does not have " "SendKeys' attribute")

    def get_text(
        self,
        locator: Optional[Locator] = None,
        *,
        search_depth: int = 8,
        timeout: Optional[float] = None,
    ) -> Optional[str]:
        """
        Get text from element (for elements which allow the GetWindowText action).

        Args:
            locator: Optional locator if it should target a child element.

            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is given.

        Returns:
            The window text of the element.

        Example:

            ```python
            from robocorp import windows
            window = windows.find_window('...')
            date = window.get_text('type:Edit name:"Date of birth"')
            ```

        Raises:
            ActionNotPossible if the text cannot be gotten from this element.
        """
        if not locator:
            element = self
        else:
            element = self.find(locator, search_depth, timeout=timeout)

        control = element.ui_automation_control
        if hasattr(control, "GetWindowText"):
            return control.GetWindowText()
        raise ActionNotPossible(
            f"Element {element!r} does not have 'GetWindowText' attribute"
        )

    @staticmethod
    def _get_value_pattern(
        item: "Control",
    ) -> Optional[Callable[[], PatternType]]:
        get_pattern: Optional[Callable] = getattr(
            item, "GetValuePattern", getattr(item, "GetLegacyIAccessiblePattern", None)
        )
        return get_pattern

    def get_value(
        self,
        locator: Optional[Locator] = None,
        *,
        search_depth: int = 8,
        timeout: Optional[float] = None,
    ) -> Optional[str]:
        """
        Get value from element (usually used with combo boxes or text controls).

        Args:
            locator: Optional locator if it should target a child element.

            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is given.

        Returns:
            The value of the element.

        Example:

            ```python
            from robocorp import windows
            window = windows.find_window('...')
            date = window.get_value('type:Edit name:"Date of birth"')
            ```

        Raises:
            ActionNotPossible if the text cannot be gotten from this element.
        """
        if not locator:
            element = self
        else:
            element = self.find(locator, search_depth, timeout=timeout)
        get_value_pattern = self._get_value_pattern(element.ui_automation_control)

        if get_value_pattern:
            func_name = get_value_pattern.__name__
            self.logger.info(
                "Retrieving the element value with the %r method.", func_name
            )
            value_pattern = get_value_pattern()
            return value_pattern.Value if value_pattern else None

        raise ActionNotPossible(
            f"Element found with {locator!r} doesn't support value retrieval"
        )

    def _set_value_with_pattern(
        self,
        value: str,
        newline_string: str,
        *,
        action: str,
        get_value_pattern: Callable[[], PatternType],
        append: bool,
        validator: Optional[Callable],
    ):
        func_name = get_value_pattern.__name__
        self.logger.info("%s the element value with the %r method.", action, func_name)
        value_pattern = get_value_pattern()
        current_value = value_pattern.Value if append else ""
        expected_value = f"{current_value}{value}{newline_string}"
        value_pattern.SetValue(expected_value)
        found_value = value_pattern.Value
        if validator and not validator(expected_value, found_value):
            raise ValueError(
                f"Couldn't set value: {expected_value!r} (value found after trying "
                f"to set_value: {found_value!r})."
            )

    def _set_value_with_keys(
        self,
        value: str,
        newline_string: str,
        *,
        action: str,
        element: "ControlElement",
        append: bool,
        locator: Optional[Locator],
        validator: Optional[Callable],
    ):
        self.logger.info(
            "%s the element value with `Send Keys`. (no patterns found)", action
        )
        if newline_string or re.search("[\r\n]", value):
            self.logger.warning(
                "The `newline` switch and EOLs are ignored when setting a value"
                " through keys! (insert them with the `enter` parameter only)"
            )
        control = element.ui_automation_control
        get_text_pattern = getattr(control, "GetTextPattern", None)

        def get_text():
            return (
                get_text_pattern().DocumentRange.GetText() if get_text_pattern else None
            )

        if append:
            current_value: str = get_text() or ""
        else:
            # Delete the entire present value inside.
            self._send_keys_to_element(control, "{Ctrl}a{Del}")
            current_value = ""
        if value:
            self._send_keys_to_element(control, value)
            actual_value = get_text()
            if actual_value is not None:
                if validator and not validator(f"{current_value}{value}", actual_value):
                    raise ValueError(
                        f"Element found with {locator!r} couldn't send value"
                        f" through keys: {value}"
                    )

    def set_value(
        self,
        value: str,
        *,
        append: bool = False,
        enter: bool = False,
        newline: bool = False,
        send_keys_fallback: bool = True,
        validator: Optional[Callable] = _SentinelValidator(),
        locator: Optional[Locator] = None,
        search_depth: int = 8,
        timeout: Optional[float] = None,
    ) -> "ControlElement":
        """
        Set the value in the element (usually used with combo boxes or
        text controls).

        Args:
            value: String value to be set.

            append: `False` for setting the value, `True` for appending it. (OFF by
                default)

            enter: Set it to `True` to press the `Enter` key at the end of the
                input. (nothing is pressed by default)

            newline: Set it to `True` to add a new line at the end of the value. (no
                EOL included by default; this won't work with `send_keys_fallback` enabled)

            send_keys_fallback: Tries to set the value by sending it through keys
                if the main way of setting it fails. (enabled by default)

            validator: Function receiving two parameters post-setting, the expected
                and the current value, which returns `True` if the two values match. (by
                default, the method will raise if the values are different, set this to
                `None` to disable validation or pass your custom function instead)

            locator: Optional locator if it should target a child element.

            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is given.

        Note:
            It is important to set `append=True` to keep the current text in the
            element. Other option is to read the current text into a
            variable, then modify that value as you wish and pass it to `set_value`
            for a complete text replacement. (without setting the `append` flag).

        Returns: The element object identified through the passed `locator` or
            this element if no `locator` was passed.

        Raises:
            ActionNotPossible: if the element does not allow the `SetValue` action
              to be run on it nor having `send_keys_fallback=True`.
            ValueError: if the new value to be set can't be set correctly.

        Example:

            ```python
            # Set value to "ab c"
            window.set_value('ab c', locator='type:DataItem name:column1')

            # Press ENTER after setting the value.
            window.set_value('console.txt', locator='type:Edit name:"File name:"', enter=True)

            # Add newline (manually) at the end of the string.
            element = window.find('name:"Text Editor"')
            element.set_value(r'abc\n')

            # Add newline with parameter.
            element.set_value('abc', newline=True)

            # Validation disabled.
            element.set_value('2nd line', append=True, newline=True, validator=None)
            ```

        Example:

            ```python
            from robocorp import windows
            window = windows.find_window('Document - WordPad')
            element = window.find('Rich Text Window')
            element.set_value(value="My text", send_keys_fallback=True)
            text = element.get_value(elem)
            print(text)
        """
        value = value or ""
        if newline and enter:
            self.logger.warning(
                "Both `newline` and `enter` switches detected, expect to see multiple"
                " new lines in the final text content."
            )
        newline_string = "\n" if newline else ""
        if not locator:
            element = self
        else:
            element = self.find(locator, search_depth, timeout=timeout)

        get_value_pattern = self._get_value_pattern(element.ui_automation_control)
        action = "Appending" if append else "Setting"

        if isinstance(validator, _SentinelValidator):
            validator = set_value_validator

        if get_value_pattern:
            self._set_value_with_pattern(
                value,
                newline_string,
                action=action,
                get_value_pattern=get_value_pattern,
                append=append,
                validator=validator,
            )
        elif send_keys_fallback:
            self._set_value_with_keys(
                value,
                newline_string,
                action=action,
                element=element,
                append=append,
                locator=locator,
                validator=validator,
            )
        else:
            raise ActionNotPossible(
                f"Element found with {locator!r} doesn't support value setting"
            )

        if enter:
            self.logger.info("Inserting a new line by sending the *Enter* key.")
            self._send_keys_to_element(
                element.ui_automation_control,
                "{Ctrl}{End}{Enter}",
                wait_time=_wait_time(),
            )

        return element

    def screenshot_pil(
        self,
        locator: Optional[Locator] = None,
        *,
        search_depth: int = 8,
        timeout: Optional[float] = None,
    ) -> Optional["Image"]:
        """
        Makes a screenshot of the given element and returns it as a PIL image.

        Args:
            locator: Optional locator if it should target a child element.

            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is given.

        Example:
            ```python
            from robocorp import windows
            img = windows.find_window('Notepad').screenshot_pil()
            if img is not None:
                ...
            ```

        Returns:
            The PIL image if it was possible to do the screenshot or None if
            it was not possible to do the screenshot.

        Raises:
            ElementNotFound if the locator was passed but it was not possible
            to find the element.
        """
        from ._screenshot import screenshot

        if not locator:
            el = self
        else:
            el = self.find(locator, search_depth, timeout)

        img = screenshot(el.ui_automation_control)
        if img is None:
            return None
        return img

    def screenshot(
        self,
        filename: Union[str, Path],
        *,
        img_format: Optional[str] = None,
        locator: Optional[Locator] = None,
        search_depth: int = 8,
        timeout: Optional[float] = None,
    ) -> Optional[str]:
        """
        Makes a screenshot of the given element and saves it into the given
        file.

        Args:
            filename: The file where the image should be saved.

            img_format: The format in which the image should be saved
                (by default detects it from the filename).

            locator: Optional locator if it should target a child element.

            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is given.

        Example:
            ```python
            from robocorp import windows
            windows.desktop().screenshot('desktop.png')
            windows.find_window('subname:Notepad').screenshot('output/notepad.png')
            ```

        Returns:
            The absolute path to the image saved or None if it was not possible
            to obtain the screenshot.

        Raises:
            ElementNotFound if the locator was passed but it was not possible
            to find the element.
        """
        import os

        img = self.screenshot_pil(
            locator=locator, search_depth=search_depth, timeout=timeout
        )
        if img is None:
            return None

        location = os.path.abspath(str(filename))
        img.save(location, img_format)
        return location

    def log_screenshot(
        self,
        level="INFO",
        *,
        locator: Optional[Locator] = None,
        search_depth: int = 8,
        timeout: Optional[float] = None,
    ) -> bool:
        """
        Makes a screenshot of the given element and saves it into the `log.html`
        using `robocorp-log`. If `robocorp-log` is not available returns False.

        Args:
            level: The log level for the screenshot.

            locator: Optional locator if it should target a child element.

            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is given.

        Returns:
            True if the screenshot was successfuly saved using `robocorp-log`
            and False otherwise.

        Example:
            ```python
            from robocorp import windows
            windows.desktop().log_screenshot('ERROR')
            ```

        Raises:
            ElementNotFound if the locator was passed but it was not possible
            to find the element.
        """

        try:
            from robocorp.log import html, suppress_variables
        except ImportError:
            return False  # If it's not available, just return.

        from ._screenshot import screenshot_as_base64png

        if not locator:
            el = self
        else:
            el = self.find(locator, search_depth, timeout=timeout)
        with suppress_variables():
            img_as_base64 = screenshot_as_base64png(el.ui_automation_control)
            if img_as_base64 is None:
                return False

            assert level in ("ERROR", "WARN", "INFO")

            html_contents = f"""<img src="data:image/png;base64,{img_as_base64}"/>"""
            html(html_contents, level)
            return True

    def set_focus(
        self,
        locator: Optional[Locator] = None,
        *,
        search_depth: int = 8,
        timeout: Optional[float] = None,
    ) -> "ControlElement":
        """
        Sets the view focus to the element (or elemen specified by the locator).

        Args:
            locator: Optional locator if it should target a child element.

            search_depth: Used as the depth to search for the locator (only
                used if the `locator` is specified).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `locator` is given.

        Example:

            ```python
            from robocorp import windows
            chrome = windows.find_window('executable:chrome')
            bt = chrome.set_focus('name:Buy type:Button')
            ```
        """
        if not locator:
            element = self
        else:
            element = self.find(locator, search_depth, timeout)
        if not hasattr(element.ui_automation_control, "SetFocus"):
            raise ActionNotPossible(
                f"Element found with {locator!r} does not have 'SetFocus' attribute"
            )
        element.ui_automation_control.SetFocus()
        return element
