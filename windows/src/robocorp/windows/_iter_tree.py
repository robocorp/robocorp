import typing
from typing import Generic, Iterator, List, Optional, TypeVar

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
        from robocorp.windows._control_element import ControlElement
        from robocorp.windows.vendored.uiautomation import Control

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
    only_depth: Optional[int] = None,
) -> Iterator[ControlTreeNode["Control"]]:
    """
    Iterates the tree as a flattened iterator (the depth is available in the node).
    Args:
        root_ctrl:
            The root control from where children should be queried.

        max_depth:
            The maximum depth for the iteration.

        only_depth:
            If given, only elements at the given depth will be returned.

    To get a nice representation it's possible to do something as:
        for control_node in iter_tree(...):
            print(control_node)
    """
    if only_depth is not None:
        max_depth = only_depth

    try:
        children = root_ctrl.GetChildren()
    except COMError:
        # Unable to get children.
        return
    depth = 1

    # First iteration
    child_pos = 0
    # Note that the depth and child index visible to the user are 1-based.
    stack: List[ControlTreeNode] = []
    for control in children:
        child_pos += 1
        node = ControlTreeNode(control, depth, child_pos, f"{child_pos}")
        stack.append(node)
        if only_depth is None or only_depth == depth:
            yield node

    while stack:  # Use stack instead of recursion (it's a bit faster).
        depth += 1
        if depth > max_depth:
            return
        next_stack: List[ControlTreeNode] = []
        for tree_node in stack:
            child_pos = 0
            try:
                children = tree_node.control.GetChildren()
            except COMError:
                continue
            parent_path = tree_node.path
            for control in children:
                child_pos += 1
                node = ControlTreeNode(
                    control, depth, child_pos, f"{parent_path}|{child_pos}"
                )
                next_stack.append(node)
                if only_depth is None or only_depth == depth:
                    yield node

        stack = next_stack
