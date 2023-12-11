import typing
from dataclasses import dataclass
from typing import Optional

from ._com_error import COMError
from .protocols import Locator

if typing.TYPE_CHECKING:
    from ._iter_tree import ControlTreeNode
    from ._vendored.uiautomation.uiautomation import Control


@dataclass
class LocationInfo:
    query_locator: Optional[Locator]
    depth: Optional[int]
    child_pos: Optional[int]
    path: Optional[str]


def build_from_locator_and_control_tree_node(
    locator: Optional[str], tree_node: "ControlTreeNode"
) -> LocationInfo:
    return LocationInfo(
        locator,
        tree_node.depth,
        tree_node.child_pos,
        tree_node.path,
    )


def empty_location_info():
    return LocationInfo(None, None, None, None)


def build_parent_location_info(location_info: LocationInfo) -> LocationInfo:
    depth = None
    if location_info.depth:
        depth = location_info.depth - 1

    # Unable to get in this case unless we actually query the parent and
    # do the search (so, the overhead is not worth it).
    child_pos = None

    path = None
    if location_info.path:
        parent_path = "|".join(location_info.path.split("|")[:-1])
        if parent_path:
            path = parent_path

    return LocationInfo(None, depth, child_pos, path)


@dataclass
class _UIAutomationControlWrapper:
    """Represent Control as dataclass"""

    __handle: int
    __pid: int
    item: "Control"
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

    def __init__(self, item: "Control", location_info: LocationInfo):
        """
        Args:
            item:
                The actual control gotten from uiautomation.

            location_info:
                This
        """
        self.item: "Control" = item
        self.location_info = location_info
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

    def get_parent(self) -> Optional["_UIAutomationControlWrapper"]:
        parent = self.item.GetParentControl()
        if parent is None:
            return None
        return _UIAutomationControlWrapper(
            parent, build_parent_location_info(self.location_info)
        )

    @property
    def path(self) -> Optional[str]:
        return self.location_info.path

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
