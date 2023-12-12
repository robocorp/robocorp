import logging
import typing
from typing import Any, Literal, Optional, Union, overload

import psutil

from ._control_element import ControlElement
from ._errors import ElementDisposed
from .protocols import Locator

if typing.TYPE_CHECKING:
    from ._ui_automation_wrapper import _UIAutomationControlWrapper

log = logging.getLogger(__name__)


def _func_return_none():
    return None


def _call_attribute_if_available(object_name, attribute_name):
    return getattr(object_name, attribute_name, _func_return_none)()


class _ExecutableNotSetSentinel:
    pass


class WindowElement(ControlElement):
    """
    Class used to interact with a window.
    """

    def __init__(self, wrapped: "_UIAutomationControlWrapper"):
        super().__init__(wrapped)
        self._executable: Union[
            _ExecutableNotSetSentinel, Optional[str]
        ] = _ExecutableNotSetSentinel()

    def __str__(self) -> str:
        # Print what can be used to build a locator.

        def fmt(s):
            s = str(s)
            if not s:
                return '""'

            if " " in s:
                s = f'"{s}"'
            return s

        try:
            handle: Any = self.handle
        except Exception:
            handle = 0

        control_type = self.control_type
        class_name = self.class_name
        name = self.name
        automation_id = self.automation_id

        try:
            pid: Any = self.pid
        except Exception:
            pid = "<unable to get>"

        try:
            executable: Any = self.executable
        except Exception:
            executable = "<unable to get>"

        info = (
            f"control:{fmt(control_type)} "
            f"class:{fmt(class_name)} "
            f"name:{fmt(name)} "
            f"id:{fmt(automation_id)} "
            f"pid:{fmt(pid)} "
            f"executable:{fmt(executable)} "
            f"handle:0x{handle:X}({handle})"
        )
        return info

    def __repr__(self):
        return f"""{self.__class__.__name__}({self.__str__()})"""

    @property
    def pid(self) -> int:
        """
        Provides the pid of the process related to the Window.

        Raises:
            COMError if the window was already disposed.
        """
        return self._wrapped.pid

    def is_active(self) -> bool:
        """
        Returns:
            True if this is currently the active window and False otherwise.
        """
        from ._vendored.uiautomation import uiautomation

        return self.handle == uiautomation.GetForegroundWindow()

    @property
    def executable(self) -> Optional[str]:
        """
        Returns:
            The executable associated to this window (or None if it was
            not possible to get it).
        """
        if isinstance(self._executable, _ExecutableNotSetSentinel):
            executable: Optional[str] = None
            try:
                from psutil import Process

                proc = Process(self.pid)
                executable = proc.exe()
                self._executable = executable
            except Exception:
                self._executable = None
        return self._executable

    @overload
    def find_child_window(
        self,
        locator: Locator,
        search_depth: int = ...,
        foreground: bool = ...,
        wait_time: Optional[float] = ...,
        timeout: Optional[float] = ...,
        raise_error: Literal[True] = ...,
    ) -> "WindowElement":
        ...

    @overload
    def find_child_window(
        self,
        locator: Locator,
        search_depth: int = ...,
        foreground: bool = ...,
        wait_time: Optional[float] = ...,
        timeout: Optional[float] = ...,
        raise_error: Literal[False] = ...,
    ) -> Optional["WindowElement"]:
        ...

    @overload
    def find_child_window(
        self,
        locator: Locator,
        search_depth: int = ...,
        foreground: bool = ...,
        wait_time: Optional[float] = ...,
        timeout: Optional[float] = ...,
        raise_error: bool = ...,
    ) -> Optional["WindowElement"]:
        ...

    def find_child_window(
        self,
        locator: Locator,
        search_depth: int = 8,
        foreground: bool = True,
        wait_time: Optional[float] = None,
        timeout: Optional[float] = None,
        raise_error: bool = True,
    ) -> Optional["WindowElement"]:
        """
        Find a child window of this window given its locator.

        Args:
            locator: The locator which should be used to find a child window.

            search_depth: The search depth to be used to find the window.

            timeout: The search for a child with the given locator will be retried
                until the given timeout (in **seconds**) elapses.
                At least one full search up to the given depth will always be done
                and the timeout will only take place afterwards.
                If not given the global config timeout will be used.

            wait_time: The time to wait after the window was found.
                If not given the global config wait_time will be used.

            foreground: If True the matched window will be made the foreground window.

            raise_error: Do not raise and return `None` when this is set to `True` and
                such a window isn't found.

        Raises:
            `ElementNotFound` if a window with the given locator could not be
            found.

        Example:

            ```python
            from robocorp import windows
            sage = windows.find_window('subname:"Sage 50" type:Window')

            # actions on the main application window
            # ...
            # get control of child window of Sage application
            child_window = sage.find_child_window('subname:"Test Company" depth:1')
            ```
        """
        from . import _find_window

        return _find_window.find_window(
            self._wrapped,
            locator,
            search_depth,
            timeout,
            wait_time,
            foreground,
            raise_error,
        )

    def foreground_window(self) -> "WindowElement":
        """
        Bring this window to the foreground (note: `find_window` makes the
        window the foreground window by default).

        Example:

            ```python
            from robocorp import windows
            calculator = windows.find_window('Calculator', foreground=False)
            ...
            calculator.foreground_window()
            ```
        """
        from . import config
        from ._find_ui_automation import _window_or_none

        window: Optional["_UIAutomationControlWrapper"] = _window_or_none(self._wrapped)
        if window is None:
            raise ElementDisposed("There is no active window")

        _call_attribute_if_available(window.item, "SetFocus")
        _call_attribute_if_available(window.item, "SetActive")
        window.item.MoveCursorToMyCenter(simulateMove=config().simulate_mouse_movement)
        return self

    def _resize_window(self, *, attribute: str) -> bool:
        attr_func = getattr(self.ui_automation_control, attribute, None)
        if attr_func:
            attr_func()
            return True
        else:
            log.warning("Element %r does not have the %r attribute", self, attribute)
            return False

    def minimize_window(self) -> bool:
        """
        Maximizes the window.

        Returns:
            True if it was possible to minimize the window and False otherwise.

        Example:

            ```python
            from robocorp import windows
            windows.find_window('executable:Spotify.exe').minimize_window()
            ```
        """
        return self._resize_window(attribute="Minimize")

    def maximize_window(self) -> bool:
        """
        Maximizes the window.

        Returns:
            True if it was possible to maximize the window and False otherwise.

        Example:

            ```python
            from robocorp import windows
            windows.find_window('executable:Spotify.exe').maximize_window()
            ```
        """
        return self._resize_window(attribute="Maximize")

    def restore_window(self) -> bool:
        """
        Restores the window.

        Returns:
            True if it was possible to restore the window and False otherwise.

        Example:

            ```python
            from robocorp import windows
            windows.find_window('executable:Spotify.exe').restore_window()
            ```
        """
        return self._resize_window(attribute="Restore")

    def set_window_pos(
        self, x: int, y: int, width: int, height: int
    ) -> "WindowElement":
        """
        Sets the window position.

        Args:
            x: The x-coordinate of the window.
            y: The y-coordinate of the window.
            width: The width of the window.
            height: The height of the window.

        Example:

            ```python
            from robocorp import windows
            desktop = windows.desktop()
            explorer = windows.find_window('executable:explorer.exe')
            # Set the size of the window to be half of the screen.
            explorer.set_window_pos(0, 0, desktop.width / 2, desktop.height)
            ```
        """
        from ._vendored.uiautomation.uiautomation import SWP, SetWindowPos

        flags = SWP.SWP_ShowWindow
        SetWindowPos(self.handle, 0, int(x), int(y), int(width), int(height), flags)
        return self

    def is_running(self) -> bool:
        """
        Returns:
            True if the pid associated to this window is still running and False
            otherwise.
        """
        from ._com_error import COMError

        try:
            pid = self.pid
        except COMError:
            return False

        try:
            if not psutil.Process(pid).is_running():
                return False
        except Exception:
            pass
        return True

    def close_window(
        self,
        use_close_button: bool = False,
        close_button_locator: Locator = "control:ButtonControl name:Close",
    ) -> bool:
        """
        Closes the windows matching the given locator.

        Note that by default the process tree will be force-killed by using the
        `pid` associated to this window. `use_close_button` can be set to True
        to try to close it by clicking on the close button (in this case any
        confirmation dialog must be explicitly handled).

        Args:
            use_close_button: If True tries to close the window by searching
                for a button with the locator: 'control:ButtonControl name:Close'
                and clicking on it (in this case any confirmation dialog must be
                explicitly handled).

            close_button_locator: Only used if `use_close_button` is True. This
                is the locator to be used to find the close button.

        Returns:
            True if the window was closed by this function and False otherwise.
        """
        from ._com_error import COMError

        if not self.is_running():
            return False  # It was closed by someone else in the meanwhile.

        if use_close_button:
            self.click(close_button_locator)
            return True

        try:
            pid = self.pid
        except COMError:
            return False
        from ._processes import kill_process_and_subprocesses

        self.logger.info("Closing window with name: %s (PID: %d)", self.name, pid)
        kill_process_and_subprocesses(pid)
        return True
