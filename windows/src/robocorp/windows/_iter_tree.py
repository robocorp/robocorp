import typing
from typing import Dict, Generic, Iterator, List, Optional, TypeVar

from _ctypes import COMError

if typing.TYPE_CHECKING:
    from PIL.Image import Image
    from robocorp.windows.vendored.uiautomation import Control

T = TypeVar("T")
Y = TypeVar("Y", covariant=True)


class ControlTreeNode(Generic[Y]):
    """
    Note: the control (Y) is usually one of the classes below.
        'uiautomation.uiautomation.Control'
        'robocorp.windows._control_element.ControlElement'
    """

    __slots__ = ["control", "depth", "child_pos", "path"]

    def __init__(self, control: Y, depth: int, child_pos: int, path: str) -> None:
        """
        Args:
            control: The control found.
            depth: The depth at which the control was found (relative to the place
                where the search was started).
            child_pos: The position in the parent at which the control was found.
            path: The path used to find the control (i.e.: '1|3|2')
        """
        self.control = control
        self.depth = depth
        self.child_pos = child_pos
        self.path = path

    def __str__(self):
        control_str = str(self.control)
        depth = self.depth

        space = " " * depth * 4
        return f"{space}{depth}-{self.child_pos}. {control_str} path:{self.path}"

    def __repr__(self):
        return f"ControlTreeNode({self.__str__()})"

    def _get_as_control(self) -> "Control":
        from robocorp.windows.vendored.uiautomation import Control

        from robocorp.windows._control_element import ControlElement

        if isinstance(self.control, ControlElement):
            ui_automation_control = self.control.ui_automation_control
            control = ui_automation_control
        else:
            assert isinstance(self.control, Control)
            control = self.control
        return control

    def screenshot(self) -> Optional["Image"]:
        """
        Returns:
            A PIL image with the contents of the bitmap.
        """

        from . import _screenshot

        control = self._get_as_control()
        return _screenshot.screenshot(control)

    def screenshot_as_base64png(self) -> Optional[str]:
        """
        Returns:
            The image with the contents as a base64 png.
        """
        from . import _screenshot

        control = self._get_as_control()
        return _screenshot.screenshot_as_base64png(control)


def iter_tree(
    root_ctrl: "Control",
    max_depth: int = 8,
    include_top: bool = True,
) -> Iterator[ControlTreeNode["Control"]]:
    """
    Iterates the tree as a flattened iterator (the depth is available in the node).
    Args:
        root_ctrl:
            The root control from where children should be queried.

        max_depth:
            The maximum depth for the iteration.

    To get a nice representation it's possible to do something as:
        for control_node in iter_tree(...):
            print(control_node)
    """
    import robocorp.windows.vendored.uiautomation as auto

    # Cache how many brothers are in total given a child. (to know child position)
    brothers_count: Dict[int, int] = {}
    # Current path in the tree as children positions. (to compute the path locator)
    children_stack: List[int] = [-1] * (max_depth + 1)

    def get_children(ctrl: "Control") -> List["Control"]:
        try:
            children = ctrl.GetChildren()
        except COMError:
            # It's possible that it was collected while doing the iteration.
            return []
        children_count = len(children)
        for child in children:
            brothers_count[id(child)] = children_count
        return children

    brothers_count[id(root_ctrl)] = 1  # the root is always singular here

    for control, depth, children_remaining in auto.WalkTree(
        root_ctrl,
        getChildren=get_children,
        includeTop=include_top,
        maxDepth=max_depth,
    ):
        child_pos = brothers_count[id(control)] - children_remaining
        children_stack[depth] = child_pos
        path = "|".join(str(pos) for pos in children_stack[1 : depth + 1])

        node = ControlTreeNode(control, depth, child_pos, path)
        yield node
