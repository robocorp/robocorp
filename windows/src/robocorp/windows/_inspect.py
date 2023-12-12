import itertools
import logging
import math
import sys
import threading
import time
import typing
from functools import partial
from typing import (
    Any,
    Callable,
    Iterator,
    List,
    Literal,
    Optional,
    Sequence,
    Set,
    Tuple,
)

import _ctypes

from ._com_error import COMError
from ._control_element import ControlElement
from ._errors import ElementNotFound
from ._window_element import WindowElement
from .protocols import Locator

if typing.TYPE_CHECKING:
    from ._iter_tree import ControlTreeNode
    from ._vendored.uiautomation.uiautomation import Control


NOT_AVAILABLE = "N/A"

log = logging.getLogger(__name__)

DEBUG = False


class _BoundsIndex:
    def __init__(self):
        self._bounds_and_obj = []

    def insert(self, bounds_rect, obj: "ControlTreeNode[ControlElement]"):
        """
        Args:
            bounds_rect: (left, top, right, bottom)
        """
        self._bounds_and_obj.append((bounds_rect, obj))

    def intersect(self, x, y) -> Iterator["ControlTreeNode[ControlElement]"]:
        for bounds_rect, obj in self._bounds_and_obj:
            left, top, right, bottom = bounds_rect
            if left <= x <= right and top <= y <= bottom:
                yield obj


def request_action(queue):
    while True:
        user_entered = input(
            """
Choose action:
print tree        (p): Prints the reachable elements that match the given filter.
                       i.e.: `p: name:"calc` will show all lines containing that 
                       substring (case independent).
                       The max depth may be customizable with max_depth=<value>
                       i.e.: p:max_depth=1 calc
highlight         (h): Highlights all elements reachable given a locator. 
                       i.e.: `h: name:"Calculator"`.
highlight mouse   (m): Highlights based on the mouse position. 
highlight all     (a): Creates highlight boxes in all the reachable elements.
select window     (s): Selects a window to inspect. Can include a filter as
                       the parameter (i.e.: s:notepad). 
quit              (q): Stops the inspection.
"""
        ).strip()

        if ":" in user_entered:
            action, params = user_entered.split(":", 1)
        else:
            action = user_entered
            params = ""

        action = action.strip()
        params = params.strip()
        if action in ("p", "print tree"):
            queue.put(("print tree", params))

        elif action in ("h", "highlight"):
            queue.put(("highlight", params))

        elif action in ("highlight mouse", "m"):
            queue.put(("highlight mouse", params))

        elif action in ("highlight all", "a"):
            queue.put(("highlight all", params))

        elif action in ("select window", "s"):
            queue.put(("select window", params))

        elif action in ("q", "quit"):
            queue.put(("quit", params))
            break

        else:
            print(f"Unable to understand command: {user_entered}")

        queue.join()


_next_id = partial(next, itertools.count(0))


class _TkHandler:
    def __init__(self):
        self._current_thread = threading.current_thread()
        self._roots = []
        # Add the default one (to interact with the loop).
        self.add_rect(0, 0, 0, 0)

    def set_rects(self, rects):
        if DEBUG:
            print(f"--- Settings {len(rects)} rects (id: {_next_id()})")
        assert self._current_thread == threading.current_thread()

        reuse_index = 1

        for rect in rects:
            if DEBUG:
                print(rect)
            left, top, right, bottom = rect

            if reuse_index < len(self._roots):
                canvas = self._roots[reuse_index]
                self.set_canvas_geometry(canvas, left, right, top, bottom)
            else:
                self.add_rect(left, right, top, bottom)

            reuse_index += 1

        while len(rects) + 1 < len(self._roots):
            if DEBUG:
                print("Destroy unused")
            self._roots.pop(-1).destroy()

        assert len(self._roots) - 1 == len(rects)

    def _create_canvas(self):
        import tkinter as tk

        root = tk.Tk()
        root.title("Inspect picker root")
        root.overrideredirect(True)  # Remove window decorations
        root.attributes("-alpha", 0.1)  # Set window transparency (0.0 to 1.0)
        root.geometry("0x0+0+0")
        root.attributes("-topmost", 1)

        from tkinter.constants import SOLID

        canvas = tk.Canvas(
            root, bg="red", highlightthickness=0, relief=SOLID, borderwidth=2
        )

        canvas.pack(fill=tk.BOTH, expand=True)
        self._roots.append(root)
        return root

    def add_rect(self, left, right, top, bottom):
        assert self._current_thread == threading.current_thread()
        canvas = self._create_canvas()
        self.set_canvas_geometry(canvas, left, right, top, bottom)

    def set_canvas_geometry(self, canvas, left, right, top, bottom):
        x = left
        w = right - x

        y = top
        h = bottom - y

        assert w >= 0, f"Found w: {w}"
        assert h >= 0, f"Found h: {h}"

        canvas.geometry(f"{w}x{h}+{x}+{y}")

    def __len__(self):
        assert self._current_thread == threading.current_thread()
        return len(self._roots) - 1  # The default one doesn't count

    @property
    def _default_root(self):
        try:
            return self._roots[0]
        except IndexError:
            return None

    def loop(self, on_loop_poll_callback: Optional[Callable[[], Any]]):
        assert self._current_thread == threading.current_thread()

        poll_5_times_per_second = int(1 / 5.0 * 1000)

        if on_loop_poll_callback is not None:

            def check_action():
                # Keep calling itself
                on_loop_poll_callback()
                default_root = self._default_root
                if default_root is not None:
                    default_root.after(poll_5_times_per_second, check_action)

            default_root = self._default_root
            if default_root is not None:
                default_root.after(poll_5_times_per_second, check_action)

        default_root = self._default_root
        if default_root is not None:
            default_root.mainloop()

    def quit(self):
        assert self._current_thread == threading.current_thread()
        self._default_root.quit()

    def destroy_tk_handler(self):
        assert self._current_thread == threading.current_thread()
        for el in self._roots:
            el.destroy()
        del self._roots[:]

    def after(self, timeout, callback):
        # Can be called from any thread
        self._default_root.after(timeout, callback)


def _extract_max_depth(params: str) -> Tuple[Optional[int], str]:
    """
    Returns the max_depth and params without the max_depth.
    """
    if params.startswith("max_depth="):
        if " " in params:
            splitted = params.split(" ", 1)
        else:
            splitted = [params, ""]

        if len(splitted) == 2:
            max_depth, params = splitted
            if max_depth.startswith("max_depth="):
                max_depth_and_level = max_depth.split("=", 1)
                if len(max_depth_and_level) == 2:
                    try:
                        return int(max_depth_and_level[1]), params
                    except Exception:
                        print(f"Invalid max_depth: {max_depth}.", file=sys.stderr)
    return None, params


class _TkHandlerThread(threading.Thread):
    """
    This is a thread-safe facade to use _TkHandler.

    The way it works is that this thread must be started and all the methods
    will actually add the actual action to a queue and then they'll return
    promptly (and later the thread should fetch the item from the queue
    and actually perform the needed operation on tk).
    """

    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.RLock()
        import queue

        self._queue: "queue.Queue[Callable[[], None]]" = queue.Queue()
        self._tk_handler: Optional[_TkHandler] = None
        self._quit_queue_loop = threading.Event()

    def run(self):
        while not self._quit_queue_loop.is_set():
            cmd = self._queue.get()
            if cmd is None:
                self._quit_queue_loop.set()
                return
            try:
                cmd()
            except Exception:
                import traceback

                traceback.print_exc()

    def dispose(self):
        self.quitloop()
        self.destroy_tk_handler()
        self._queue.put_nowait(None)  # Finishes the thread.

    def destroy_tk_handler(self):
        def destroy_tk_handler():
            with self._lock:
                if self._tk_handler is None:
                    return
                self._tk_handler.destroy_tk_handler()
                self._tk_handler = None

        self._queue.put_nowait(destroy_tk_handler)

    def add_rect(self, left, right, top, bottom):
        def add_rect():
            tk_handler = self._tk_handler
            if tk_handler is not None:
                self._tk_handler.add_rect(left, right, top, bottom)

        self._queue.put_nowait(add_rect)

    def set_rects(self, rects) -> threading.Event:
        """
        Returns:
            An event called after the rects were actually updated.
        """
        ev = threading.Event()

        def set_rects():
            try:
                tk_handler = self._tk_handler
                if tk_handler is not None:
                    tk_handler.set_rects(rects)
            finally:
                ev.set()

        self._queue.put_nowait(set_rects)
        return ev

    def loop(self):
        def loop():
            tk_handler = self._tk_handler
            if tk_handler is not None:

                def on_loop_poll_callback():
                    # This will be continually called in the tk loop.
                    # We use it to check whether something was added
                    # to the queue (so that the user can quit the
                    # loop for instance).
                    import queue

                    try:
                        cmd = self._queue.get_nowait()
                    except queue.Empty:
                        return

                    if cmd is None:
                        self._quit_queue_loop.set()
                        return

                    try:
                        cmd()
                    except Exception:
                        import traceback

                        traceback.print_exc()

                self._tk_handler.loop(on_loop_poll_callback)

        self._queue.put_nowait(loop)

    def create(self):
        def create():
            with self._lock:
                if self._tk_handler is not None:
                    self._tk_handler.destroy_tk_handler()
                    self._tk_handler = None
                self._tk_handler = _TkHandler()

        self._queue.put_nowait(create)

    def quitloop(self):
        def quitloop():
            with self._lock:
                tk_handler = self._tk_handler
                if tk_handler is not None:
                    tk_handler.quit()

        self._queue.put_nowait(quitloop)


class PickedInspectorElementError(Exception):
    """
    This error is thrown when the inspector picks one of the widgets
    related to highlighting.
    """


class PickedElementNotInParentHierarchy(Exception):
    """
    This error is thrown when the picked element is not in the hierarchy
    of the passed parent.
    """


class UnreachableElementInParentHierarchy(Exception):
    """
    This error is thrown when it's possible to get to the parent a path from
    a picked control, but it's not possible to get to the picked control from
    the parent using the tree hierarchy (i.e.: Control.GetChildren() can't
    get to it).
    """

    def __init__(
        self,
        msg: str,
        parent: ControlElement,
        hierarchy: List["Control"],
        partial_match: List["ControlElement"],
    ) -> None:
        """
        Args:
            msg: The error message.
            parent: The parent which was used to scope down the search.
            hierarchy: The hierarchy found -- note that it does not include the
                parent, it contains the hierarchy of controls.
            partial_match: The partial elements that could be found in the hierarchy.
        """
        Exception.__init__(self, msg)
        self.parent = parent
        self.hierarchy = hierarchy
        self.partial_match = partial_match


def build_parent_hierarchy(
    control: ControlElement, up_to_parent: Optional[ControlElement]
) -> List["ControlTreeNode[ControlElement]"]:
    """
    Builds the parent hierarchy from the given control up to the given parent.

    If the parent cannot be found the return is empty.

    Args:
        control: The leaf element.
        up_to_parent: The hierarchy will be built up to this element.

    Returns:
        A list containing the ControlElements to reach the given control
        from the given parent (note that the parent itself will not be
        included in the return, but the control will be).

    Raises:
        PickedInspectorElementError: if an internal widget is highlighted.
        PickedElementNotInParentHierarchy: if the element was not found in the
            parent hierarchy.
        UnreachableElementInParentHierarchy: if the element is not reachable from
            the hierarchy.
    """
    from ._find_ui_automation import get_desktop_element
    from ._iter_tree import ControlTreeNode
    from ._ui_automation_wrapper import LocationInfo, _UIAutomationControlWrapper
    from ._vendored.uiautomation.uiautomation import ControlsAreSame

    if up_to_parent is None:
        up_to_parent = ControlElement(get_desktop_element())

    hierarchy: List["Control"] = []
    curr: Optional["Control"] = control._wrapped.item
    if DEBUG:
        print("build_parent_hierarchy")
        print("found control", curr)
    while curr is not None:
        if curr.Name == "Inspect picker root":
            raise PickedInspectorElementError()
        hierarchy.append(curr)
        curr = curr.GetParentControl()
        if DEBUG:
            print("found control", curr)
        if curr and ControlsAreSame(curr, up_to_parent._wrapped.item):
            # This must be the last one in the hierarchy for searching
            # for indexes afterwards.
            hierarchy.append(curr)
            break
    else:
        # Oops, the given parent wasn't found.
        raise PickedElementNotInParentHierarchy(
            f"It was not possible to find the given parent "
            f"({str(up_to_parent).strip()} in the hierarchy "
            f"of: {str(control).strip()}"
        )
        return []

    found = []
    if hierarchy:
        hierarchy = list(reversed(hierarchy))
        path = ""
        for depth, c in enumerate(hierarchy):
            if depth == 0:
                continue  # Skip the 'up_to_parent'.
            prev = hierarchy[depth - 1]

            find_element = hierarchy[depth]

            children = prev.GetChildren()
            for child_pos, child in enumerate(children):
                if ControlsAreSame(child, find_element):
                    child_pos += 1  # It's one-based.
                    if not path:
                        path = f"{child_pos}"
                    else:
                        path = f"{path}|{child_pos}"

                    location_info = LocationInfo(None, depth, child_pos, path)
                    el = ControlElement(_UIAutomationControlWrapper(c, location_info))
                    found.append(ControlTreeNode(el, depth, child_pos, path))
                    break
            else:
                location_info = LocationInfo(None, depth, None, None)
                child_not_found = ControlElement(
                    _UIAutomationControlWrapper(c, location_info)
                )

                raise UnreachableElementInParentHierarchy(
                    f"It was not possible to find the given child:\n"
                    f"({str(child_not_found).strip()}\nas a child "
                    f"of:\n{str(control).strip()}",
                    up_to_parent,
                    hierarchy,
                    [x.control for x in found],
                )

    return found


class CursorPos:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def as_tuple(self):
        return self.x, self.y

    def distance_to(self, cursor: "CursorPos"):
        dx = self.x - cursor.x
        dy = self.y - cursor.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance

    def consider_same_as(self, cursor: Optional["CursorPos"]):
        if cursor is None:
            return False
        return self.distance_to(cursor) <= 3

    def __str__(self):
        return f"CursorPos({self.x}, {self.y})"

    __repr__ = __str__


class _PickerThread(threading.Thread):
    def __init__(
        self,
        tk_handler_thread: _TkHandlerThread,
        control_element: ControlElement,
        on_pick,
    ) -> None:
        threading.Thread.__init__(self)

        self._stop_event = threading.Event()
        self.on_pick = on_pick
        self.control_element = control_element
        self._tk_handler_thread = tk_handler_thread

    def _found_from_cursor_pos(
        self, cursor_pos: Tuple[int, int], parent: Optional[ControlElement]
    ) -> List["ControlTreeNode[ControlElement]"]:
        """
        Args:
            parent: if None gets up to the desktop

        Raises:
            PickedInspectorElementError: if an internal widget is highlighted.
            PickedElementNotInParentHierarchy: if the element was not found in the
                parent hierarchy.
            UnreachableElementInParentHierarchy: if the element is not reachable from
                the hierarchy.
        """
        from ._ui_automation_wrapper import (
            _UIAutomationControlWrapper,
            empty_location_info,
        )
        from ._vendored import uiautomation

        try:
            control = uiautomation.ControlFromPoint(*cursor_pos)
        except COMError:
            return []
        else:
            if control is None:
                return []
            return build_parent_hierarchy(
                ControlElement(
                    _UIAutomationControlWrapper(control, empty_location_info())
                ),
                parent,
            )

    def _found_from_cursor_pos_with_point_in_parent(
        self,
        parent: Optional[ControlElement] = None,
        cursor: Optional[Tuple[int, int]] = None,
        visited_handles: Optional[Set[int]] = None,
        depth: int = 1,
        parent_path: str = "",
    ) -> Iterator["ControlTreeNode[ControlElement]"]:
        """
        Note that this code isn't working (abandoned for now).
        """
        from ._iter_tree import ControlTreeNode
        from ._ui_automation_wrapper import LocationInfo, _UIAutomationControlWrapper
        from ._vendored import uiautomation
        from ._vendored.uiautomation.uiautomation import ControlsAreSame

        if parent is None:
            parent = self.control_element
            parent.update_geometry()

        if cursor is None:
            cursor = uiautomation.GetCursorPos()

        if visited_handles is None:
            visited_handles = set()

        left = parent.left
        top = parent.top
        x_in_parent = cursor[0] - left
        y_in_parent = cursor[1] - top
        try:
            children = parent._wrapped.item.GetChildren()

            # XXX is the parent.handle the proper handle to pass?
            control = uiautomation.ControlFromPointInParent(
                parent.handle, x_in_parent, y_in_parent
            )
            if control is None or ControlsAreSame(control, parent._wrapped.item):
                return
            for child_pos, c in enumerate(children):
                if ControlsAreSame(c, control):
                    child_pos += 1
                    break
            else:
                print(f"Unable to find child index for: {control}", file=sys.stderr)
                return
        except _ctypes.COMError:
            pass  # Ignore, if the user is out of bounds it'll be raised.
        else:
            if not parent_path:
                path = f"{child_pos}"
            else:
                path = f"{parent_path}|{child_pos}"
            location_info = LocationInfo(None, depth, child_pos, path)
            el = ControlTreeNode(
                ControlElement(_UIAutomationControlWrapper(control, location_info)),
                depth,
                child_pos,
                path,
            )

            yield el
            yield from self._found_from_cursor_pos_with_point_in_parent(
                el.control, cursor, visited_handles, depth, path
            )

    def _do_pick(
        self, cursor_pos: CursorPos
    ) -> Optional[List["ControlTreeNode[ControlElement]"]]:
        """
        Returns the elements found in the given cursor position.
        """
        ev = self._tk_handler_thread.set_rects([])
        ev.wait(0.1)

        initial_time = time.monotonic()
        timeout_at = initial_time + 5
        while True:
            try:
                # This approach has a shortcoming in that if
                # we create our own decoration widgets it can
                # end up getting our own widgets instead of
                # the ones we'd like to inspect!
                # Due to this we first hide the contents and
                # then request it.
                return self._found_from_cursor_pos(
                    cursor_pos.as_tuple(), parent=self.control_element
                )

                # Not working (this could be nicer as the UI doesn't need to be
                # actually top-level and thus the tk decorations wouldn't be
                # picked by it).
                # self.control_element.update_geometry()
                # return list(
                #     self._found_from_cursor_pos_with_point_in_parent(
                #         self.control_element, cursor_pos.as_tuple()
                #     )
                # )

            except (
                PickedInspectorElementError,
                COMError,
            ):
                # If we picked the inspector itself or something changed in the
                # meanwhile, this didn't work.
                if time.monotonic() > timeout_at:
                    return None
                time.sleep(0.1)
            except (
                PickedElementNotInParentHierarchy,
                UnreachableElementInParentHierarchy,
            ):
                return []

    def run(self) -> None:
        try:
            self._run()
        except Exception:
            import traceback

            traceback.print_exc()

    def _run(self) -> None:
        from ._vendored.uiautomation.uiautomation import (
            GetCursorPos,
            UIAutomationInitializerInThread,
        )

        DEBOUNCE_TIME = 0.3
        with UIAutomationInitializerInThread(debug=False):
            last_cursor_pos = CursorPos(*GetCursorPos())
            cursor_time = time.monotonic()
            last_pick_pos = None

            while True:
                if self._stop_event.wait(0.13):
                    break

                cursor_pos = CursorPos(*GetCursorPos())
                if cursor_pos.consider_same_as(last_pick_pos):
                    # If we did a pick at this position, don't do anything until the
                    # user moves the mouse.
                    continue

                if not cursor_pos.consider_same_as(last_cursor_pos):
                    # Clear the rects
                    ev = self._tk_handler_thread.set_rects([])
                    ev.wait(0.2)
                    cursor_time = time.monotonic()
                    last_cursor_pos = cursor_pos
                    continue

                if (time.monotonic() - cursor_time) > DEBOUNCE_TIME:
                    cursor_time = time.monotonic()
                else:
                    # Still close, but wait for the debounce time
                    continue

                found = self._do_pick(cursor_pos)
                last_cursor_pos = CursorPos(*GetCursorPos())
                if not last_cursor_pos.consider_same_as(cursor_pos):
                    # The position changed in the meanwhile, start things over
                    continue
                last_pick_pos = last_cursor_pos

                if found and not self._stop_event.is_set():
                    self.on_pick(found)
                    # If we haven't found we don't even need to remove the
                    # rects as the picker itself did that.
                    new_rects = [f.control.rectangle for f in found[-1:]]
                    ev = self._tk_handler_thread.set_rects(new_rects)
                    ev.wait(0.2)

    def stop(self):
        self._stop_event.set()


class ElementInspector:
    def __init__(self, control_element: ControlElement):
        self.control_element = control_element
        self._tk_handler_thread: _TkHandlerThread = _TkHandlerThread()
        self._tk_handler_thread.start()
        self._picker_thread: Optional[_PickerThread] = None
        self._current_thread = threading.current_thread()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()

    def _check_thread(self):
        if self._current_thread != threading.current_thread():
            raise AssertionError(
                f"Error. Expected to be run in thread: {self._current_thread}."
                f"Current thread: {threading.current_thread()}"
            )

    def dispose(self):
        self._check_thread()
        self._tk_handler_thread.dispose()

    def start_highlight(
        self,
        locator: Optional[Locator] = None,
        search_depth: int = 8,
        timeout: Optional[float] = None,
        search_strategy: Literal["siblings", "all"] = "all",
    ) -> Sequence["ControlElement"]:
        """
        Args:
            locator: If passed, entries matching the given locator will be highlighted.
            search_depth: Up to which depth entries should be highlighted.
            timeout: Timeout (in **seconds**) to find a locator.
            search_strategy: After finding a locator, should only siblings be found
              or should a full tree traversal be done?

        Returns:
            The elements found which matched the given locator.

        Note:
            The stop_highlight must always be called afterwards (both to stop
            highlighting and to exit the tk loop).
        """
        self._check_thread()
        self._tk_handler_thread.destroy_tk_handler()
        self._tk_handler_thread.create()

        matches: Sequence[ControlElement]
        if locator:
            try:
                matches = self.control_element.find_many(
                    locator,
                    search_depth,
                    timeout,
                    search_strategy,
                    wait_for_element=False,
                )
            except ElementNotFound:
                matches = ()
        else:
            matches = ()

        tk_handler_thread = self._tk_handler_thread
        rects = []
        for control_element in matches:
            if not control_element.has_valid_geometry():
                continue
            left, top, right, bottom = control_element.rectangle
            rects.append((left, top, right, bottom))

        tk_handler_thread.set_rects(rects)
        tk_handler_thread.loop()
        return matches

    def stop_highlight(self) -> None:
        self._check_thread()
        self._tk_handler_thread.quitloop()
        self._tk_handler_thread.destroy_tk_handler()

    def list_windows(self) -> List[WindowElement]:
        self._check_thread()
        from . import desktop

        return desktop().find_windows("regex:.*")

    def start_picking(self, on_pick):
        self._check_thread()
        assert self._picker_thread is None, "Error. A picking is already in place."
        self.start_highlight(None)
        self._picker_thread = _PickerThread(
            self._tk_handler_thread, self.control_element, on_pick
        )
        self._picker_thread.start()

    def stop_picking(self):
        self._check_thread()
        self._picker_thread.stop()
        self._picker_thread.join()
        self._picker_thread = None
        self.stop_highlight()

    def _interact_select_window(self, filter_str):
        available = self.list_windows()

        print("Available windows:")
        for i, window in enumerate(available):
            if filter_str:
                if filter_str.lower() in str(window).lower():
                    print(f"{i}: {window}")
            else:
                print(f"{i}: {window}")

        choice = input(
            "Please enter the index of the window to be inspected:\n"
        ).strip()
        try:
            choice_i = int(choice)
        except ValueError:
            print(
                "Error. Unable to understand which window should be "
                "inspected (please provide the number of the window "
                "to be inspected)."
            )
        else:
            try:
                control = available[choice_i]
            except IndexError:
                print("Error. Invalid index.")
            else:
                self.control_element = control

    def _interact_print_filter(self, params):
        kwargs = {}
        max_depth, params = _extract_max_depth(params)
        if max_depth:
            kwargs["max_depth"] = max_depth
        params = params.lower().strip()
        for child in self.control_element._iter_children_nodes(**kwargs):
            s = str(child)
            if params in s.lower():
                print(s)

    def _print_highlight(self, found_matches: Sequence[ControlElement]):
        print("Highlighting elements:")
        elements_with_invalid_bounds = []
        for m in found_matches:
            if m.has_valid_geometry():
                left, top, right, bottom = m.rectangle
                print(f"{m} (left:{left}, right:{right}, top:{top}, bottom:{bottom})")
            else:
                elements_with_invalid_bounds.append(m)

        if elements_with_invalid_bounds:
            print("Elements with invalid bounds (NOT highlighted):")
            for m in elements_with_invalid_bounds:
                print(m)
        input("Press enter to stop highlighting\n")

    def inspect(self) -> None:
        from queue import Queue

        queue: "Queue[Tuple[str, str]]" = Queue()
        threading.Thread(target=request_action, args=(queue,)).start()

        while True:
            action, params = queue.get()
            # action, params = "highlight mouse", ""
            try:
                if action == "quit":
                    print("Stopping inspect.")
                    self.dispose()
                    break

                elif action == "select window":
                    self._interact_select_window(params)

                elif action == "print tree":
                    self._interact_print_filter(params)

                elif action == "highlight all":
                    found_matches = self.start_highlight("regex:.*")
                    try:
                        if not found_matches:
                            print("No elements found.")
                        else:
                            self._print_highlight(found_matches)

                    finally:
                        self.stop_highlight()

                elif action == "highlight":
                    locator = params
                    found_matches = self.start_highlight(locator)
                    try:
                        if not found_matches:
                            print("No elements found.")
                        else:
                            self._print_highlight(found_matches)
                    finally:
                        self.stop_highlight()

                elif action == "highlight mouse":
                    handle = self.control_element.handle
                    if not handle:
                        print(
                            "Error, the current inspected element does not "
                            "have an associated handle."
                        )
                    else:
                        next_i = partial(next, itertools.count())

                        def on_pick(found):
                            if not found:
                                print("No element found")
                            else:
                                print(
                                    f"\n=== Found new element (pick: "
                                    f"{next_i()}) ==="
                                )
                                for f in found:
                                    print(f)

                            print("Press enter to stop highlighting\n")

                        self.start_picking(on_pick)
                        try:
                            input("Press enter to stop highlighting\n")
                        finally:
                            self.stop_picking()

            finally:
                queue.task_done()
