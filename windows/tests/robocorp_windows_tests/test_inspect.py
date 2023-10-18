import sys
import threading

from robocorp.windows._window_element import WindowElement


def test_iter_windows_and_screenshot(calculator_window_element: WindowElement) -> None:
    found_img = False
    tree_elements = tuple(calculator_window_element.iter_children(max_depth=8))
    for element in tree_elements:
        img = element.screenshot_pil()
        found_img = found_img or img is not None

    assert len(tree_elements) > 10
    assert found_img


def test_build_hierarchy(tk_process):
    import io

    from robocorp.windows import find_window
    from robocorp.windows._inspect import build_parent_hierarchy

    window = find_window('name:"Tkinter Elements Showcase"')
    bt = window.find("class:Button path:1|5")
    found = []
    for c in build_parent_hierarchy(bt, window):
        found.append(
            f"{c.control.control_type} {c.control.class_name} "
            f"path:{c.path} {c.control.location_info}"
        )

    assert found == [
        (
            "PaneControl TkChild path:1 LocationInfo("
            "query_locator=None, depth=1, child_pos=1, path='1')"
        ),
        (
            "ButtonControl Button path:1|5 LocationInfo("
            "query_locator=None, depth=2, child_pos=5, path='1|5')"
        ),
    ]

    stream = io.StringIO()
    window.print_tree(stream=stream)
    for c in build_parent_hierarchy(bt, window):
        assert str(c) in stream.getvalue()


def test_inspect(calculator_window_element: WindowElement):
    import time

    from robocorp.windows import desktop
    from robocorp.windows._inspect import ElementInspector

    with ElementInspector(desktop()) as element_inspector:
        assert (
            len([x for x in element_inspector.list_windows() if x.name == "Calculator"])
            == 1
        )
    # return

    with ElementInspector(calculator_window_element) as element_inspector:
        # element_inspector.inspect()
        debug = False
        sleep_time = 2
        # element_inspector.inspect()
        element_inspector.start_highlight("regex:.*")
        try:
            if debug:
                print("highlighting all...")
                time.sleep(sleep_time)
                print("end highlighting all...")
        finally:
            element_inspector.stop_highlight()

        # element_inspector.print_tree_str()

        element_inspector.start_highlight("control:TextControl")
        try:
            if debug:
                print("highlighting 'control:TextControl'...")
                time.sleep(sleep_time)
                print("end highlighting 'control:TextControl'...")
        finally:
            element_inspector.stop_highlight()


def test_inspect_user_picks(calculator_window_element: WindowElement):
    from robocorp.windows._inspect import ElementInspector
    from robocorp.windows._vendored.uiautomation.uiautomation import SetCursorPos

    with ElementInspector(calculator_window_element) as element_inspector:
        ev = threading.Event()

        found_elements = []

        def on_pick(found):
            found_elements.append(found)
            ev.set()

        # Check for new and old version of Windows.
        el = calculator_window_element.find(
            "name:Zero or (name:0 control:ButtonControl)", timeout=0.3
        )

        element_inspector.start_picking(on_pick)
        try:
            SetCursorPos(el.xcenter, el.ycenter)
            ev.wait(5)
            assert found_elements
            found = found_elements[-1]
            leaf = found[-1]
            assert leaf.control.handle == el.handle
            assert leaf.control.is_same_as(el)

            # Check if the path is also correct
            assert calculator_window_element.find(
                f"path:{leaf.control.path}"
            ).is_same_as(el)

            # Check that the first item is just below the given parent.
            first_found = found[0]
            parent = first_found.control.get_parent()
            assert calculator_window_element.is_same_as(parent)

            assert leaf.control.path
            parent = leaf.control.get_parent()
            assert parent.path

            assert parent.path == leaf.control.path.rsplit("|", 1)[0]
        except Exception:
            sys.stderr.write("Error happened in test. Printing tree:\n")
            calculator_window_element.print_tree()

            raise
        finally:
            element_inspector.stop_picking()
