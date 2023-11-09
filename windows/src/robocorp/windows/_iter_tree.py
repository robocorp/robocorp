import typing
from typing import Generic, Iterator, Optional, Set, TypeVar

from ._com_error import COMError

if typing.TYPE_CHECKING:
    from ._vendored.uiautomation import Control

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
        return f"{space}{depth}-{self.child_pos}. {control_str}"

    def __repr__(self):
        return f"ControlTreeNode({self.__str__()})"


def iter_tree(
    root_ctrl: "Control",
    max_depth: int = 8,
    only_depths: Optional[Set[int]] = None,
) -> Iterator[ControlTreeNode["Control"]]:
    """
    Iterates the tree as a flattened iterator (the depth is available in the node).
    Args:
        root_ctrl:
            The root control from where children should be queried.

        max_depth:
            The maximum depth for the iteration.

        only_depths:
            If given, only elements at the given depths will be returned
            (1-based indexes)

    To get a nice representation it's possible to do something as:
        for control_node in iter_tree(...):
            print(control_node)
    """
    if only_depths is not None:
        max_depth = max(only_depths)

    # This code could be used to do a breadth first search (by default
    # we do a depth first search).
    # try:
    #     children = root_ctrl.GetChildren()
    # except COMError:
    #     # Unable to get children.
    #     return
    # depth = 1
    #
    # # First iteration
    # child_pos = 0
    # # Note that the depth and child index visible to the user are 1-based.
    # stack: List[ControlTreeNode] = []
    # for control in children:
    #     child_pos += 1
    #     node = ControlTreeNode(control, depth, child_pos, f"{child_pos}")
    #     stack.append(node)
    #     if only_depth is None or only_depth == depth:
    #         yield node
    #
    # while stack:  # Use stack instead of recursion (it's a bit faster).
    #     depth += 1
    #     if depth > max_depth:
    #         return
    #     next_stack: List[ControlTreeNode] = []
    #     for tree_node in stack:
    #         child_pos = 0
    #         try:
    #             children = tree_node.control.GetChildren()
    #         except COMError:
    #             continue
    #         parent_path = tree_node.path
    #         for control in children:
    #             child_pos += 1
    #             node = ControlTreeNode(
    #                 control, depth, child_pos, f"{parent_path}|{child_pos}"
    #             )
    #             next_stack.append(node)
    #             if only_depth is None or only_depth == depth:
    #                 yield node
    #
    #     stack = next_stack

    # Algorithm to do a depth-first search without recursion. This is the
    # default because it's how we want to present the tree to the user when we
    # print it.
    depth = 0
    try:
        children = root_ctrl.GetChildren()
    except COMError:
        return

    child_list = [(_ContainerView(children), "", len(children))]

    while depth >= 0:
        last_items, parent_path, children_len = child_list[-1]
        if last_items:
            child_pos = children_len - len(last_items) + 1
            if parent_path:
                use_path = f"{parent_path}|{child_pos}"
            else:
                use_path = f"{child_pos}"
            curr = last_items.popleft()
            node = ControlTreeNode(curr, depth + 1, child_pos, use_path)
            if only_depths is None:
                yield node
            elif (depth + 1) in only_depths:
                yield node
            if depth + 1 < max_depth:
                try:
                    children = curr.GetChildren()
                except COMError:
                    pass
                else:
                    if children:
                        depth += 1
                        child_list.append(
                            (_ContainerView(children), use_path, len(children))
                        )
        else:
            del child_list[depth]
            depth -= 1


class _ContainerView:
    # A bit of an optimization: because lists in python are actually arrays
    # removing from position 0 can be slow, so, we create a container view
    # which will not really remove it, instead it'll just increment the
    # first visible position. Better than a deque because we'd need to create
    # it from the list which can be slow.

    def __init__(self, lst):
        self.first = 0
        self._lst = lst

    def popleft(self):
        self.first += 1
        return self._lst[self.first - 1]

    def __len__(self):
        return len(self._lst) - self.first
