import time
import typing
from typing import Iterator, List, Optional

from robocorp.windows._control_element import ControlElement
from robocorp.windows.protocols import Locator

if typing.TYPE_CHECKING:
    from robocorp.windows._iter_tree import ControlTreeNode
    from robocorp.windows._window_element import WindowElement


class Desktop(ControlElement):
    def __init__(self):
        from robocorp.windows._config_uiautomation import _config_uiautomation
        from robocorp.windows._find_ui_automation import find_ui_automation_wrapper

        _config_uiautomation()

        ControlElement.__init__(self, find_ui_automation_wrapper("desktop"))

    # Overridden just to change the default max_depth to 1
    def print_tree(
        self, stream=None, show_properties: bool = False, max_depth: int = 1
    ) -> None:
        return ControlElement.print_tree(
            self, stream=stream, show_properties=show_properties, max_depth=max_depth
        )

    def iter_children(
        self, *, max_depth: int = 1
    ) -> Iterator["ControlTreeNode[ControlElement]"]:
        return ControlElement.iter_children(self, max_depth=max_depth)

    def find_window(
        self,
        locator: Locator,
        search_depth: int = 1,
        timeout: Optional[float] = None,
        wait_time: Optional[float] = None,
        foreground: bool = True,
    ) -> "WindowElement":
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
            timeout: The timeout to be used to search for windows (note: only
                used if `wait_for_window` is `True`).
            wait_for_window: Defines whether the search should keep on searching
                until a window with the given locator is found (note that if True
                and no window was found a ElementNotFound is raised).
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
        Closes the windows matching the given locator.

        Args:
            locator: The locator which should be used to find windows to be closed.
            search_depth: The search depth to be used to find windows (by default
                equals 1, meaning that only top-level windows will be closed).
                Note that windows are closed by force-killing the pid related
                to the window.
            wait_time: A time to wait after closing each window.

        Returns:
            The number of closed windows.
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
        Use Windows Run window to launch an application.

        Activated by pressing `Win + R`. Then the app name is typed in and finally the
        "Enter" key is pressed.

        Args:
            text: Text to enter into the Run input field. (e.g. `Notepad`)
            wait_time: Time to sleep after the searched app is executed. (1s by
                default)
        """

        # NOTE(cmin764): The waiting time after each key set sending can be controlled
        #  globally and individually with `Set Wait Time`.
        self.send_keys(keys="{Win}r")
        self.send_keys(keys=text, interval=0.01)
        self.send_keys(send_enter=True)
        time.sleep(wait_time)

    def windows_search(self, text: str, wait_time: float = 3.0) -> None:
        """
        Use Windows search window to launch application.

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
