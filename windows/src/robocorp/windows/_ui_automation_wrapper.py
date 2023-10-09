import typing
from dataclasses import dataclass
from typing import Optional

from _ctypes import COMError

from robocorp.windows.protocols import Locator

if typing.TYPE_CHECKING:
    from robocorp.windows.vendored.uiautomation.uiautomation import Control


@dataclass
class _UIAutomationControlWrapper:
    """Represent Control as dataclass"""

    __handle: int
    __pid: int
    item: "Control"
    locator: Optional[Locator] = None
    name: str = ""
    automation_id: str = ""
    control_type: str = ""
    class_name: str = ""
    left: int = -1
    right: int = -1
    top: int = -1
    bottom: int = -1
    width: int = -1
    height: int = -1
    xcenter: int = -1
    ycenter: int = -1

    def __init__(self, item: "Control", locator: Optional[Locator]):
        """
        Args:
            item:
                The actual control gotten from uiautomation.

            locator:
                The locator str -- when gotten from iterating the tree
                it'd be something as `path:1|1|1`, but when getting it with
                a _find_ui_automation_wrapper it'd be the locator passed as the query.
        """
        self.item: "Control" = item
        self.locator: Optional[Locator] = locator
        try:
            self.name = item.Name
        except COMError:
            self.name = "<disposed>"

        try:
            self.automation_id = item.AutomationId
        except COMError:
            self.automation_id = "<disposed>"

        try:
            self.control_type = item.ControlTypeName
        except COMError:
            self.control_type = "<disposed>"
        try:
            self.class_name = item.ClassName
        except COMError:
            self.class_name = "<disposed>"

        self.update_geometry()

    def is_disposed(self) -> bool:
        try:
            self.item.Name
        except COMError:
            return True
        else:
            return False

    @property
    def handle(self) -> int:
        try:
            return self.__handle
        except AttributeError:
            self.__handle = self.item.NativeWindowHandle
        return self.__handle

    @property
    def pid(self) -> int:
        try:
            return self.__pid
        except AttributeError:
            self.__pid = self.item.ProcessId
        return self.__pid

    def update_geometry(self):
        # If there's no rectangle, then all coords are defaulting to -1.
        try:
            rect = self.item.BoundingRectangle
        except COMError:
            rect = None
        if rect:
            self.left = rect.left
            self.right = rect.right
            self.top = rect.top
            self.bottom = rect.bottom
            self.width = rect.width()
            self.height = rect.height()
            self.xcenter = rect.xcenter()
            self.ycenter = rect.ycenter()
        else:
            self.left = (
                self.right
            ) = (
                self.top
            ) = (
                self.bottom
            ) = self.width = self.height = self.xcenter = self.ycenter = -1
