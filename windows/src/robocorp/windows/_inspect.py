import sys
import threading
import time
import typing
from contextlib import contextmanager
from io import StringIO
from typing import Any, Callable, Dict, Iterator, List, Literal, Optional, Tuple

from robocorp.windows._control_element import ControlElement
from robocorp.windows._window_element import WindowElement
from robocorp.windows.protocols import Locator

if typing.TYPE_CHECKING:
    from robocorp.windows._iter_tree import ControlTreeNode


NOT_AVAILABLE = "N/A"


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
print tree        (p): Prints the tree of reachable elements.
                       The depth may be customized with max_depth=<value>.
                       i.e.: p:max_depth=1
filter            (f): Prints the reachable elements that match the given filter.
                       i.e.: `f: name:"Calc` will show all lines 
                       containing that substring.
                       The max depth may be customizable with max_depth=<value>
                       i.e.: f:max_depth=1 name:"Calc
highlight         (h): Highlights all elements reachable given a locator. 
                       i.e.: `h: name:"Calculator"`.
highlight mouse   (m): Highlights based on the mouse position. 
highlight all     (a): Creates highlight boxes in all the reachable elements.
select window     (w): Selects a window to inspect. 
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
        if action in ("f", "filter"):
            queue.put(("filter", params))

        elif action in ("p", "print tree"):
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


def wait_for_input(msg, on_input):
    try:
        input(msg)
    finally:
        on_input()


class _TkHandler:
    def __init__(self):
        self._current_thread = threading.current_thread()
        self._roots = []
        # Add the default one (to interact with the loop).
        self._reset_rects = False
        self._reused_index = 1
        self.add_rect(0, 0, 0, 0)

    @contextmanager
    def reset_rects(self):
        assert self._current_thread == threading.current_thread()
        self._reset_rects = True
        self._reused_index = 1  # The one at 0 is always kept
        yield
        while self._reused_index < len(self._roots):
            self._roots.pop(-1).destroy()

    def add_rect(self, left, right, top, bottom):
        assert self._current_thread == threading.current_thread()
        if self._reset_rects and len(self._roots) > self._reused_index:
            root = self._roots[self._reused_index]
            self._reused_index += 1
        else:
            import tkinter as tk

            root = tk.Tk()
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

        x = left
        w = right - x

        y = top
        h = bottom - y

        assert w >= 0
        assert y >= 0

        root.geometry(f"{w}x{h}+{x}+{y}")

    def __len__(self):
        assert self._current_thread == threading.current_thread()
        return len(self._roots) - 1  # The default one doesn't count

    @property
    def _default_root(self):
        return self._roots[0]

    def loop(self, on_loop_poll_callback: Optional[Callable[[], Any]]):
        assert self._current_thread == threading.current_thread()

        poll_15_times_per_second = int(1 / 15.0) * 1000

        def check_action():
            # Keep calling itself
            on_loop_poll_callback()
            self._default_root.after(poll_15_times_per_second, check_action)

        self._default_root.after(poll_15_times_per_second, check_action)

        self._default_root.mainloop()

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
            cmd()

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

    def loop(self):
        def loop():
            tk_handler = self._tk_handler
            if tk_handler is not None:

                def on_loop_poll_callback():
                    import queue

                    try:
                        cmd = self._queue.get_nowait()
                    except queue.Empty:
                        return True  # Reschedule

                    # A command was found. Don't reschedule.
                    if cmd is None:
                        self._quit_queue_loop.set()
                        return False
                    else:
                        cmd()
                        return False

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


class ElementInspector:
    def __init__(self, control_element: ControlElement):
        self.control_element = control_element
        self._tk_handler_thread: _TkHandlerThread = _TkHandlerThread()
        self._tk_handler_thread.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()

    def dispose(self):
        self._tk_handler_thread.dispose()

    def print_tree_str(self, params: str = ""):
        kwargs: Dict[str, Any] = {}
        max_depth, params = _extract_max_depth(params)
        if max_depth:
            kwargs["max_depth"] = max_depth
        self.control_element.print_tree(**kwargs)

    def start_highlight(
        self,
        locator: Locator,
        search_depth: int = 8,
        timeout: Optional[float] = None,
        search_strategy: Literal["siblings", "all"] = "all",
    ) -> bool:
        if locator is None:
            # If not given, highlight everything.
            locator = "regex:.*"

        self._tk_handler_thread.destroy_tk_handler()
        self._tk_handler_thread.create()

        matches = self.control_element.find_all(
            locator, search_depth, timeout, search_strategy, wait_for_element=False
        )
        if not matches:
            return False

        tk_handler_thread = self._tk_handler_thread
        for control_element in matches:
            left, top, right, bottom = control_element.rectangle
            tk_handler_thread.add_rect(left, right, top, bottom)

        tk_handler_thread.loop()
        return True

    def stop_highlight(self) -> None:
        self._tk_handler_thread.quitloop()
        self._tk_handler_thread.destroy_tk_handler()

    def list_windows(self) -> List[WindowElement]:
        from robocorp.windows import desktop

        return desktop().find_windows("regex:.*")

    def inspect(self) -> None:
        from queue import Queue

        import robocorp.windows.vendored.uiautomation as auto

        queue: "Queue[Tuple[str, str]]" = Queue()
        threading.Thread(target=request_action, args=(queue,)).start()

        while True:
            action, params = queue.get()
            try:
                if action == "quit":
                    print("Stopping inspect.")
                    self.dispose()
                    break

                elif action == "select window":
                    available = self.list_windows()

                    print("Available windows:")
                    for i, window in enumerate(available):
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

                elif action == "print tree":
                    self.print_tree_str(params)

                elif action == "filter":
                    kwargs = {}
                    max_depth, params = _extract_max_depth(params)
                    if max_depth:
                        kwargs["max_depth"] = max_depth
                    for child in self.control_element.iter_children(**kwargs):
                        s = str(child)
                        if params in s:
                            print(s)

                elif action == "highlight all":
                    tk_handler = _TkHandler()

                    n_elements_found = 0
                    initial_time = base_time = time.monotonic()
                    for control_tree_node in self.control_element.iter_children():
                        n_elements_found += 1
                        if time.monotonic() - base_time > 2:
                            print(
                                f"Already found: {n_elements_found} elements "
                                f"(elapsed: {time.monotonic()-initial_time:.1f}s)."
                            )
                            base_time = time.monotonic()
                        left, top, right, bottom = control_tree_node.control.rectangle
                        if left == -1 and top == -1 and right == -1 and bottom == -1:
                            print(
                                f"Element skipped (invalid bounds): {control_tree_node}"
                            )
                            continue

                        tk_handler.add_rect(left, right, top, bottom)

                    if len(tk_handler) == 0:
                        print("No bounds found.")
                    else:
                        print(f"Number elements found: {n_elements_found}.")
                        input_event = threading.Event()

                        def on_input():
                            tk_handler.quit()
                            input_event.set()

                        threading.Thread(
                            target=wait_for_input,
                            args=("Press enter to stop highlighting\n", on_input),
                        ).start()

                        while not input_event.is_set():
                            tk_handler.loop(None)

                    tk_handler.destroy_tk_handler()

                elif action == "highlight":
                    locator = params

                    matches = self.control_element.find_all(
                        locator, search_strategy="all"
                    )
                    n_skipped = 0

                    if not matches:
                        print("No matching elements found.")
                    else:
                        tk_handler = _TkHandler()
                        for control_element in matches:
                            left, top, right, bottom = control_element.rectangle
                            if (
                                left == -1
                                and top == -1
                                and right == -1
                                and bottom == -1
                            ):
                                n_skipped += 1
                                print(
                                    f"Element skipped (invalid bounds): "
                                    f"{control_element}"
                                )
                                continue

                            tk_handler.add_rect(left, right, top, bottom)

                        if len(tk_handler) == 0:
                            print("No bounds found.")
                        else:
                            print(
                                f"Number elements found: {len(matches)} "
                                f"(skipped: {n_skipped})."
                            )
                            input_event = threading.Event()

                            def on_input():
                                tk_handler.quit()
                                input_event.set()

                            threading.Thread(
                                target=wait_for_input,
                                args=("Press enter to stop highlighting\n", on_input),
                            ).start()

                            while not input_event.is_set():
                                tk_handler.loop(None)

                        tk_handler.destroy_tk_handler()

                elif action == "highlight mouse":
                    input_event = threading.Event()
                    threading.Thread(
                        target=wait_for_input,
                        args=(
                            "Press enter to stop highlighting\n",
                            input_event.set,
                        ),
                    ).start()

                    tk_handler = _TkHandler()
                    last_printed = ""
                    last_i = 0

                    # Collect the structure
                    bounds_index = _BoundsIndex()

                    for child in self.control_element.iter_children():
                        bounds_index.insert(child.control.rectangle, child)

                    def compute_new_highlight():
                        if input_event.is_set():
                            tk_handler.quit()
                            return
                        nonlocal last_printed
                        nonlocal last_i
                        x, y = auto.GetCursorPos()

                        with tk_handler.reset_rects():
                            stream = StringIO()
                            for control_tree_node in bounds_index.intersect(x, y):
                                (
                                    left,
                                    top,
                                    right,
                                    bottom,
                                ) = control_tree_node.control.rectangle
                                tk_handler.add_rect(left, right, top, bottom)
                                print(control_tree_node, file=stream)

                        new_to_print = stream.getvalue().strip()
                        if new_to_print:
                            if new_to_print != last_printed:
                                last_i += 1
                                print(f"\n=== Found new element (pick: {last_i}) ===")
                                print(new_to_print)
                                print("Press enter to stop highlighting\n")
                                last_printed = new_to_print

                        tk_handler.after(50, compute_new_highlight)

                    tk_handler.after(50, compute_new_highlight)
                    while not input_event.is_set():
                        tk_handler.loop(None)
                    tk_handler.destroy_tk_handler()

            finally:
                queue.task_done()
