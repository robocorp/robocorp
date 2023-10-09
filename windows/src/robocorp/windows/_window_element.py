import logging
import typing
from typing import Any, Optional, Union

import psutil
from _ctypes import COMError

from robocorp.windows._control_element import ControlElement
from robocorp.windows._errors import ElementDisposed
from robocorp.windows.protocols import Locator

if typing.TYPE_CHECKING:
    from robocorp.windows._ui_automation_wrapper import _UIAutomationControlWrapper

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
        from robocorp.windows.vendored.uiautomation import uiautomation

        return self.handle == uiautomation.GetForegroundWindow()

    @property
    def executable(self) -> Optional[str]:
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

    def find_child_window(
        self,
        locator: Locator,
        search_depth: int = 8,
        foreground: bool = True,
        wait_time: Optional[float] = None,
        timeout: Optional[float] = None,
    ) -> "WindowElement":
        """Get control of child window of the active window
        by locator.

        :param locator: string locator or Control element
        :param foreground: True to bring window to foreground
        :param wait_time: time to wait after activeting a window
        :param timeout: float value in seconds, see keyword
         ``Set Global Timeout``
        :return: _UIAutomationControlWrapper object

        Example:

        .. code-block:: robotframework

            Control Window   subname:"Sage 50" type:Window
            # actions on the main application window
            # ...
            # get control of child window of Sage application
            Control Child Window   subname:"Test Company" depth:1
        """
        from robocorp.windows import _find_window

        return _find_window.find_window(
            self._wrapped,
            locator,
            search_depth,
            timeout,
            wait_time,
            foreground,
        )

    def foreground_window(self) -> "_UIAutomationControlWrapper":
        """Bring the current active window or the window defined
        by the locator to the foreground.

        :param locator: string locator or Control element
        :return: _UIAutomationControlWrapper object

        Example:

        .. code-block:: robotframework

            ${window}=  Foreground Window   Calculator
        """
        from robocorp.windows import config
        from robocorp.windows._find_ui_automation import _window_or_none

        window: Optional["_UIAutomationControlWrapper"] = _window_or_none(self._wrapped)
        if window is None:
            raise ElementDisposed("There is no active window")

        _call_attribute_if_available(window.item, "SetFocus")
        _call_attribute_if_available(window.item, "SetActive")
        window.item.MoveCursorToMyCenter(simulateMove=config().simulate_mouse_movement)
        return window

    def _resize_window(self, *, attribute: str) -> bool:
        attr_func = getattr(self.ui_automation_control, attribute, None)
        if attr_func:
            attr_func()
            return True
        else:
            log.warning("Element %r does not have the %r attribute", self, attribute)
            return False

    def minimize_window(self) -> bool:
        """Minimize the current active window or the window defined
        by the locator.

        :param locator: string locator or element
        :return: `_UIAutomationControlWrapper` object

        Example:

        .. code-block:: robotframework

            ${window} =    Minimize Window  # Current active window
            Minimize Window    executable:Spotify.exe
        """
        return self._resize_window(attribute="Minimize")

    def maximize_window(self) -> bool:
        """Maximize the current active window or the window defined
        by the locator.

        :param locator: string locator or element
        :return: `_UIAutomationControlWrapper` object

        Example:

        .. code-block:: robotframework

            ${window} =    Maximize Window  # Current active window
            Maximize Window    executable:Spotify.exe
        """
        return self._resize_window(attribute="Maximize")

    def restore_window(self) -> bool:
        """Window restore the current active window or the window
        defined by the locator.

        :param locator: string locator or element
        :return: `_UIAutomationControlWrapper` object

        Example:

        .. code-block:: robotframework

            ${window} =    Restore Window  # Current active window
            Restore Window    executable:Spotify.exe
        """
        return self._resize_window(attribute="Restore")

    def close_window(self) -> bool:
        from robocorp.windows._processes import kill_process_and_subprocesses

        try:
            pid = self.pid
        except COMError:
            return False  # It was closed by someone else in the meanwhile.

        try:
            if not psutil.Process(pid).is_running():
                return False
        except Exception:
            pass

        self.logger.info("Closing window with name: %s (PID: %d)", self.name, pid)
        kill_process_and_subprocesses(pid)
        return True
