import time
import typing
from typing import Iterator, List, Literal, Optional, overload

from ._control_element import ControlElement
from .protocols import Locator

if typing.TYPE_CHECKING:
    from ._iter_tree import ControlTreeNode
    from ._vendored.uiautomation.uiautomation import Control
    from ._window_element import WindowElement


class Desktop(ControlElement):
    """
    The desktop is the control, containing other top-level windows.

    The elements provided by robocorp-windows are organized as:
        Desktop (root control)
            WindowElement (top-level windows)
                ControlElement (controls inside a window)
    """

    def __init__(self) -> None:
        from ._config_uiautomation import _config_uiautomation
        from ._find_ui_automation import (
            LocatorStrAndOrSearchParams,
            find_ui_automation_wrapper,
        )

        _config_uiautomation()

        from ._match_ast import collect_search_params

        locator = "desktop"
        locator_and_or_search_params = LocatorStrAndOrSearchParams(
            locator, collect_search_params(locator)
        )
        ControlElement.__init__(
            self, find_ui_automation_wrapper(locator_and_or_search_params)
        )

    # Overridden just to change the default max_depth to 1
    def print_tree(
        self, stream=None, show_properties: bool = False, max_depth: int = 1
    ) -> None:
        """
        Print a tree of control elements.

        A Windows application structure can contain multilevel element structure.
        Understanding this structure is crucial for creating locators. (based on
        controls' details and their parent-child relationship)

        This keyword can be used to output logs of application's element structure.

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
            windows.find_window("Calculator").find("path:2|3").print_tree()
            ```
        """

        return ControlElement.print_tree(
            self, stream=stream, show_properties=show_properties, max_depth=max_depth
        )

    def _iter_children_nodes(
        self, *, max_depth: int = 1
    ) -> Iterator["ControlTreeNode[ControlElement]"]:
        """
        Internal API to provide structure with a `ControlTreeNode` for printing.
        Not part of the public API (should not be used by client code).
        """
        return ControlElement._iter_children_nodes(self, max_depth=max_depth)

    def iter_children(self, *, max_depth: int = 1) -> Iterator["ControlElement"]:
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
        return ControlElement.iter_children(self, max_depth=max_depth)

    @overload
    def find_window(
        self,
        locator: Locator,
        search_depth: int = ...,
        timeout: Optional[float] = ...,
        wait_time: Optional[float] = ...,
        foreground: bool = ...,
        raise_error: Literal[True] = ...,
    ) -> "WindowElement":
        ...

    @overload
    def find_window(
        self,
        locator: Locator,
        search_depth: int = ...,
        timeout: Optional[float] = ...,
        wait_time: Optional[float] = ...,
        foreground: bool = ...,
        raise_error: Literal[False] = ...,
    ) -> Optional["WindowElement"]:
        ...

    @overload
    def find_window(
        self,
        locator: Locator,
        search_depth: int = ...,
        timeout: Optional[float] = ...,
        wait_time: Optional[float] = ...,
        foreground: bool = ...,
        raise_error: bool = ...,
    ) -> Optional["WindowElement"]:
        ...

    def find_window(
        self,
        locator: Locator,
        search_depth: int = 1,
        timeout: Optional[float] = None,
        wait_time: Optional[float] = None,
        foreground: bool = True,
        raise_error: bool = True,
    ) -> Optional["WindowElement"]:
        """
        Finds windows matching the given locator.

        Args:
            locator: The locator which should be used to find a window.

            search_depth: The search depth to be used to find the window (by default
                equals 1, meaning that only top-level windows will be found).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.

            wait_time: The time to wait after the windows was found.
                If not given the global config wait_time will be used.

            foreground: If True the matched window will be made the foreground window.

            raise_error: Do not raise and return `None` when this is set to `True` and
                such a window isn't found.

        Raises:
            `ElementNotFound` if a window with the given locator could not be found.
        """
        from . import _find_window

        return _find_window.find_window(
            None, locator, search_depth, timeout, wait_time, foreground, raise_error
        )

    def find_windows(
        self,
        locator: Locator,
        search_depth: int = 1,
        timeout: Optional[float] = None,
        wait_for_window: bool = False,
    ) -> List["WindowElement"]:
        """
        Finds windows matching the given locator.

        Args:
            locator: The locator which should be used to find windows (if not
                given, all windows are returned).

            search_depth: The search depth to be used to find windows (by default
                equals 1, meaning that only top-level windows will be found).

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.
                Only used if `wait_for_window` is True.

            wait_for_window: Defines whether the search should keep on searching
                until a window with the given locator is found (note that if True
                and no window was found a ElementNotFound is raised).

        Returns:
            The `WindowElement`s which should be used to interact with the window.

        Example:

            ```python
            window = find_windows('Calculator')
            window = find_windows('name:Calculator')
            window = find_windows('subname:Notepad')
            window = find_windows('regex:.*Notepad')
            window = find_windows('executable:Spotify.exe')
            ```
        """
        from . import _find_window

        self._convert_locator_to_locator_and_or_search_params(locator)
        return _find_window.find_windows(
            None, locator, search_depth, timeout, wait_for_window, search_strategy="all"
        )

    def close_windows(
        self,
        locator: Locator,
        search_depth: int = 1,
        timeout: Optional[float] = None,
        wait_for_window: bool = False,
        wait_time: Optional[float] = 0,
        use_close_button: bool = False,
        close_button_locator: Locator = "control:ButtonControl name:Close",
    ) -> int:
        """
        Closes the windows matching the given locator.

        Note that by default the process tree will be force-killed by using the
        `pid` associated to the window. `use_close_button` can be set to True
        to try to close it by clicking on the close button (in this case any
        confirmation dialog must be explicitly handled).

        Args:
            locator: The locator which should be used to find windows to be closed.

            search_depth: The search depth to be used to find windows (by default
                equals 1, meaning that only top-level windows will be closed).
                Note that windows are closed by force-killing the pid related
                to the window.

            timeout: The search for a window with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to
                the given depth will always be done and the timeout will only
                take place afterwards (if `wait_for_window` is True).
                Only used if `wait_for_window` is True.
                If not given the global config timeout will be used.

            wait_for_window: If True windows this method will keep searching for
                windows until a window is found or until the timeout is reached
                (an ElementNotFound is raised if no window was found until the
                timeout is reached, otherwise an empty list is returned).

            wait_time: A time to wait after closing each window.

            use_close_button: If True tries to close the window by searching
                for a button with the locator: 'control:ButtonControl name:Close'
                and clicking on it (in this case any confirmation dialog must be
                explicitly handled).

            close_button_locator: Only used if `use_close_button` is True. This
                is the locator to be used to find the close button.

        Returns:
            The number of closed windows.

        Raises:
            ElementNotFound: if wait_for_window is True and the timeout was reached.
        """

        from . import config

        windows_elements = self.find_windows(
            locator, search_depth, timeout=timeout, wait_for_window=wait_for_window
        )

        if wait_time is None:
            wait_time = config().wait_time

        closed = 0
        for element in windows_elements:
            if element.close_window(
                use_close_button=use_close_button,
                close_button_locator=close_button_locator,
            ):
                closed += 1
                if wait_time:
                    time.sleep(wait_time)
        return closed

    def windows_run(self, text: str, wait_time: float = 1) -> None:
        """
        Use Windows `Run window` to launch an application.

        Activated by pressing `Win + R`. Then the app name is typed in and finally the
        "Enter" key is pressed.

        Args:
            text: Text to enter into the Run input field. (e.g. `Notepad`)
            wait_time: Time to sleep after the searched app is executed. (1s by
                default)
        """

        # NOTE(cmin764): The waiting time after each key set sending can be controlled
        #  globally and individually with the config wait_time.
        self.send_keys(keys="{Win}r")
        self.send_keys(keys=text, interval=0.01)
        self.send_keys(send_enter=True)
        time.sleep(wait_time)

    def windows_search(self, text: str, wait_time: float = 3.0) -> None:
        """
        Use Windows `search window` to launch application.

        Activated by pressing `win + s`.

        Args:
            text: Text to enter into search input field (e.g. `Notepad`)
            wait_time: sleep time after search has been entered (default 3.0 seconds)
        """
        search_cmd = "{Win}s"
        if self.get_win_version() == "11":
            search_cmd = search_cmd.rstrip("s")
        self.send_keys(search_cmd)
        self.send_keys(text)
        self.send_keys("{Enter}")
        time.sleep(wait_time)

    @staticmethod
    def get_win_version() -> str:
        """
        Windows only utility which returns the current Windows major version.

        Returns:
            The current Windows major version (i.e.: '10', '11').
        """
        # Windows terminal `ver` command is bugged, until that's fixed, check by build
        #  number. (the same applies for `platform.version()`)
        import platform

        WINDOWS_11_BUILD = 22000
        WINDOWS_10 = "10"
        WINDOWS_11 = "11"

        version_parts = platform.version().split(".")
        major = version_parts[0]

        if major == WINDOWS_10 and int(version_parts[2]) >= WINDOWS_11_BUILD:
            major = WINDOWS_11

        return major

    def wait_for_active_window(
        self,
        locator: Locator,
        timeout: Optional[float] = None,
        wait_time: Optional[float] = None,
    ) -> "WindowElement":
        """
        Waits for a window with the given locator to be made active.

        Args:
            locator: The locator that the active window must match.
            timeout: Timeout (in **seconds**) to wait for a window with the given
                locator to be made active.
            wait_time: A time to wait after the active window is found.

        Raises:
            ElementNotFound if no window was found as active until the timeout
            was reached.

        Note: if there's a matching window which matches the locator but it's not
            the active one, this will fail (consider using `find_window`
            for this use case).
        """
        from . import config
        from ._errors import ElementNotFound
        from ._find_ui_automation import _matches
        from ._find_window import restrict_to_window_locators
        from ._iter_tree import ControlTreeNode
        from ._match_ast import SearchParams, collect_search_params
        from ._match_common import SearchType
        from ._ui_automation_wrapper import (
            _UIAutomationControlWrapper,
            empty_location_info,
        )
        from ._vendored.uiautomation.uiautomation import GetForegroundControl
        from ._window_element import WindowElement

        or_search_params_by_level = collect_search_params(locator)
        if len(or_search_params_by_level) > 1:
            raise ValueError(
                f"The locator passed ({locator!r}) can only have one "
                "level in this API ('>' not allowed)."
            )

        if timeout is None:
            timeout = config().timeout

        or_search_params = or_search_params_by_level[0]

        search_params: SearchType
        for s in or_search_params.parts:
            assert isinstance(s, SearchParams)
            search_params = s.search_params
            if "depth" in search_params:
                raise ValueError('"depth" locator not valid for this API.')
            if "path" in search_params:
                raise ValueError('"path" locator not valid for this API.')
            if "desktop" in search_params:
                raise ValueError('"desktop" locator not valid for this API.')

        restrict_to_window_locators((or_search_params,))

        timeout_at = time.monotonic() + timeout
        while True:
            control = GetForegroundControl()
            while control is not None:
                if control.GetParentControl() is None:
                    # We don't want to check the desktop itself
                    break

                for part in or_search_params.parts:
                    assert isinstance(part, SearchParams)
                    search_params = part.search_params

                    tree_node: "ControlTreeNode[Control]" = ControlTreeNode(
                        control, 0, 0, ""
                    )
                    if _matches(search_params, tree_node):
                        el = WindowElement(
                            _UIAutomationControlWrapper(control, empty_location_info())
                        )

                        if wait_time is None:
                            wait_time = config().wait_time
                        time.sleep(wait_time)

                        return el

                control = control.GetParentControl()

            if time.monotonic() > timeout_at:
                # Check only after at least one search was done.
                msg = (
                    "No active window was found as active with the locator: "
                    f"{locator!r}."
                )

                if control is not None:
                    el = WindowElement(
                        _UIAutomationControlWrapper(control, empty_location_info())
                    )
                    msg += f"\nActive window: {el}"
                else:
                    msg += "\nNo active window found."

                curr_windows = self.find_windows("regex:.*")
                if curr_windows:
                    msg += "\nExisting Windows:\n"
                    for w in curr_windows:
                        msg += f"{w}\n"

                self.log_screenshot()
                raise ElementNotFound(msg)
            else:
                time.sleep(1 / 15.0)

    def drag_and_drop(
        self,
        source: "ControlElement",
        target: "ControlElement",
        speed: float = 1.0,
        hold_ctrl: Optional[bool] = False,
        wait_time: float = 1.0,
    ):
        """Drag and drop the source element into target element.

        Args:
            source: Source element for the operation.
            target: Target element for the operation
            speed: The speed at which the mouse should move to make the drag
                (1 means regular speed, values bigger than 1 mean that
                the mouse should move faster and values lower than 1 mean that
                the mouse should move slower).
            hold_ctrl: Whether the `Ctrl` key should be hold while doing the
                drag and drop (on some cases this means that a copy of
                the item should be done).
            wait_time: Time to wait after drop, defaults to 1.0 second.

        Example:

            ```python
            # Get the opened explorer on the c:\\temp folder
            from robocorp import windows
            explorer1 = windows.find_window(r'name:C:\temp executable:explorer.exe')
            explorer2 = windows.find_window(r'name:C:\temp2 executable:explorer.exe')

            # copying a file, report.html, from source (File Explorer) window
            # into a target (File Explorer) Window
            report_html = explorer1.find('name:report.html type:ListItem')
            items_view = explorer2.find('name:"Items View"')
            explorer.drag_and_drop(report_html, items_view, hold_ctrl=True)
            ```
        """
        from ._vendored import uiautomation as auto

        try:
            if hold_ctrl:
                auto.PressKey(auto.Keys.VK_CONTROL)
            auto.DragDrop(
                source.xcenter,
                source.ycenter,
                target.xcenter,
                target.ycenter,
                moveSpeed=speed,
                waitTime=wait_time,
            )
        finally:
            if hold_ctrl:
                auto.ReleaseKey(auto.Keys.VK_CONTROL)
