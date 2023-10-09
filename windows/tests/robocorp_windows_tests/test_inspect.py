from robocorp.windows._window_element import WindowElement


def test_iter_windows_and_screenshot(calculator_window_element: WindowElement) -> None:
    found_img = False
    tree_elements = tuple(calculator_window_element.iter_children(max_depth=16))
    for element in tree_elements:
        img = element.screenshot()
        found_img = found_img or img is not None

    assert len(tree_elements) > 10
    assert found_img


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
