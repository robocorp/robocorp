import time
import typing
from typing import Iterator, List, Optional

from robocorp.windows._control_element import ControlElement
from robocorp.windows.protocols import Locator

if typing.TYPE_CHECKING:
    from robocorp.windows._iter_tree import ControlTreeNode
    from robocorp.windows._window_element import WindowElement


class Desktop(ControlElement):
    """
    The desktop is the control, containing other top-level windows.

    The elements provided by robocorp-windows are organized as:
        Desktop (root control)
            WindowElement (top-level windows)
                ControlElement (controls inside a window)
    """

    def __init__(self):
        from robocorp.windows._config_uiautomation import _config_uiautomation
        from robocorp.windows._find_ui_automation import find_ui_automation_wrapper

        _config_uiautomation()

        ControlElement.__init__(self, find_ui_automation_wrapper("desktop"))

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

    def find_window(
        self,
        locator: Locator,
        search_depth: int = 1,
        timeout: Optional[float] = None,
        wait_time: Optional[float] = None,
        foreground: bool = True,
    ) -> "WindowElement":
        """
        Finds windows matching the given locator.

        Args:
            locator: The locator which should be used to find a window.

            search_depth: The search depth to be used to find the window (by default
                equals 1, meaning that only top-level windows will be found).

            timeout:
                The search for a child with the given locator will be retried
                until the given timeout elapses.

                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.

                If not given the global config timeout will be used.

            wait_time:
                The time to wait after the windows was found.

                If not given the global config wait_time will be used.

            foreground:
                If True the matched window will be made the foreground window.

        Raises:
            ElementNotFound if a window with the given locator could not be
            found.
        """
        from robocorp.windows import _find_window

        return _find_window.find_window(
            None, locator, search_depth, timeout, wait_time, foreground
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

            timeout:
                The search for a child with the given locator will be retried
                until the given timeout elapses.

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
        from robocorp.windows import _find_window

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
    ) -> int:
        """
        Closes the windows matching the given locator. Note that internally
        this will force-kill the processes with the related `pid` as well
        as all of the child processes of that `pid`.

        Args:
            locator: The locator which should be used to find windows to be closed.

            search_depth: The search depth to be used to find windows (by default
                equals 1, meaning that only top-level windows will be closed).
                Note that windows are closed by force-killing the pid related
                to the window.

            timeout:
                The search for a window with the given locator will be retried
                until the given timeout elapses. At least one full search up to
                the given depth will always be done and the timeout will only
                take place afterwards (if `wait_for_window` is True).

                Only used if `wait_for_window` is True.

                If not given the global config timeout will be used.

            wait_for_window: If True windows this method will keep searching for
                windows until a window is found or until the timeout is reached
                (an ElementNotFound is raised if no window was found until the
                timeout is reached, otherwise an empty list is returned).

            wait_time: A time to wait after closing each window.

        Returns:
            The number of closed windows.

        Raises:
            ElementNotFound: if wait_for_window is True and the timeout was reached.
        """

        from robocorp.windows import config

        windows_elements = self.find_windows(
            locator, search_depth, timeout=timeout, wait_for_window=wait_for_window
        )

        if wait_time is None:
            wait_time = config().wait_time

        closed = 0
        for element in windows_elements:
            if element.close_window():
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
        self.send_keys(None, search_cmd)
        self.send_keys(None, text)
        self.send_keys(None, "{Enter}")
        time.sleep(wait_time)

    def get_win_version(self) -> str:
        """
        Windows only utility which returns the current Windows major version.
        """
        # Windows terminal `ver` command is bugged, until that's fixed, check by build
        #  number. (the same applies for `platform.version()`)
        import platform

        version_parts = platform.version().split(".")
        major = version_parts[0]
        if major == "10" and int(version_parts[2]) >= 22000:
            major = "11"

        return major
