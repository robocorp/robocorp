import io
from typing import Dict

import pytest

from robocorp.windows import find_window
from robocorp.windows._errors import ElementNotFound
from robocorp.windows._window_element import WindowElement


def test_get_icon_from_file():
    from robocorp.windows import get_icon_from_file

    assert get_icon_from_file("C:\\Windows\\System32\\calc.exe") is not None


def test_iter_windows_and_screenshot(calculator_window_element: WindowElement) -> None:
    found_img = False
    tree_elements = tuple(calculator_window_element.iter_children(max_depth=8))
    for element in tree_elements:
        img = element.screenshot_pil()
        found_img = found_img or img is not None

    assert len(tree_elements) > 10
    assert found_img


def test_find_window_verbose_error(calculator_window_element: WindowElement) -> None:
    window = find_window("name:Calculator")
    assert window

    with pytest.raises(ElementNotFound) as err:
        find_window("name:NameNotThere", timeout=0.01)

    s = str(err.value)
    assert "Found Windows:" in s
    assert "name:Calculator" in s
    assert "control:WindowControl" in s


def test_inspector_process(calculator_window_element: WindowElement) -> None:
    from robocorp.windows._find_ui_automation import (
        find_ui_automation_wrapper,
        find_ui_automation_wrappers,
    )
    from robocorp.windows._ui_automation_wrapper import _UIAutomationControlWrapper

    # Ok, we have the tree structure for the calc elements. Now, given
    # an element we have to highlight it in the calculator.
    #
    # The basic idea is the following:
    #
    # 1. An application (window) is chosen.
    #
    # 2. A (control) tree is created from that window.
    #
    # 3. Users are expected to:
    #     - Apply locators to the tree (so that filtering will take place to show
    #       items matching and the parent structure).
    #     - Click items on the tree to see their properties to create a locator.
    #
    # Get the element by the name
    assert calculator_window_element.name == "Calculator"
    calculator_window = find_ui_automation_wrapper("name:Calculator")
    assert calculator_window.item.NativeWindowHandle == calculator_window_element.handle

    # Get by the handle
    assert (
        find_ui_automation_wrapper(
            f"handle:{calculator_window.item.NativeWindowHandle}"
        ).item.NativeWindowHandle
        == calculator_window_element.handle
    )

    # Get the element by the executable
    assert (
        find_ui_automation_wrapper(
            f"executable:{calculator_window_element.executable}"
        ).item.NativeWindowHandle
        == calculator_window_element.handle
    )

    try:
        version_with_path = True
        number_pad = find_ui_automation_wrapper('name:Calculator > name:"Number pad"')
        assert number_pad
        buttons_in = number_pad
    except ElementNotFound:
        # On Github actions, Microsoft Windows Server 2022, 10.0.20348 the calculator
        # isn't the same (it doesn't have the "Number pad")
        # So, use different locators.
        version_with_path = False
        buttons_in = find_ui_automation_wrapper("name:Calculator > path:1|3")
        assert buttons_in

    name_to_bt: Dict[str, _UIAutomationControlWrapper] = {}
    for el in find_ui_automation_wrappers("class:Button", root_element=buttons_in):
        name_to_bt[el.name] = el

    if version_with_path:
        # Now, get the buttons below the number pad.
        # In this version of calculator we have a "Zero" button with a "0" text.
        assert set(name_to_bt).issuperset(
            {
                "Zero",
                "One",
                "Two",
                "Three",
                "Four",
                "Five",
                "Six",
                "Seven",
                "Eight",
                "Nine",
                "Decimal separator",
            }
        )
        name_zero = "name:Zero"
    else:
        # In this version there's just a button with the text directly.
        name_zero = "name:0"
        assert set(name_to_bt).issuperset(
            {
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
            }
        )

    # Check class strategy getting sibling elements.
    name_to_bt = {}
    for el in find_ui_automation_wrappers("class:Button", root_element=buttons_in):
        name_to_bt[el.name] = el
        assert el.location_info.query_locator == "class:Button"

    assert len(find_ui_automation_wrappers(name_zero, root_element=buttons_in)) == 1

    # Test the path strategy (note: for the version without the path we already
    # used a path strategy before).
    if version_with_path:
        number_pad_path = ""
        five_path = ""
        for element in calculator_window_element.iter_children(max_depth=16):
            if element.name == "Number pad":
                number_pad_path = element.path
            elif element.name == "5":
                five_path = element.path

        assert five_path.startswith(number_pad_path)
        subpath = five_path[len(number_pad_path) + 1 :]
        el_five = find_ui_automation_wrapper(f"path:{subpath}", root_element=number_pad)
        assert el_five.name == "5"


def test_find_click_print_tree(calc_process) -> None:
    from io import StringIO

    from robocorp import windows

    window = windows.find_window("name:Calculator")
    assert window is not None

    stream = StringIO()
    window.print_tree(stream)
    found = stream.getvalue()

    windows.config().verbose_errors = False
    assert "name:Calculator" in found
    assert "1-1. " in found

    try:
        window.click("id:clearButton")
    except ElementNotFound:
        window.click("name:Clear")
    window.send_keys(keys="96+4=")

    with pytest.raises(ElementNotFound) as e:
        window.click("id:this_is_not_there", timeout=0)

    msg = str(e.value)
    assert "control:TextControl" not in msg

    with pytest.raises(ElementNotFound):
        window.find("name:this_is_not_there", timeout=0)

    try:
        result = window.find("name:Result", timeout=0)
    except ElementNotFound:
        windows.config().verbose_errors = True
        result = window.find("id:CalculatorResults", timeout=0)
        windows.config().verbose_errors = False

    # Check verbose errors.
    windows.config().verbose_errors = True
    with pytest.raises(ElementNotFound) as e:
        window.find("name:this_is_not_there", timeout=0)

    msg = str(e.value)
    assert "control:TextControl" in msg
    assert "name:100" in msg

    stream = io.StringIO()
    result.print_tree(stream, show_properties=True)
    result.log_screenshot()
    val = stream.getvalue()

    # Depends on which calc version is available.
    if "get_text() = '100'" not in val:
        assert "get_attribute('Name') = 100" in val
        assert "get_value() = ''" in val
        assert "get_text() = None" in val


@pytest.fixture
def _clear_notepad_entries():
    from robocorp import windows

    windows.desktop().close_windows("executable:notepad.exe")
    yield
    windows.desktop().close_windows("executable:notepad.exe")


def test_usage(_clear_notepad_entries):
    from robocorp import windows

    windows.desktop().windows_run("notepad.exe", wait_time=0)
    w = windows.find_window("executable:notepad.exe", timeout=4)
    assert w is not None

    # windows.desktop().inspect()

    # w.inspect()
