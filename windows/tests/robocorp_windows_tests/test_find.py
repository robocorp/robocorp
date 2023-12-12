from typing import Dict, List

import pytest


def test_find_windows():
    from robocorp_windows_tests.fixtures import wait_for_condition

    from robocorp import windows
    from robocorp.windows._errors import ElementNotFound

    windows.desktop().close_windows("name:Calculator")
    assert len(windows.find_windows("name:Calculator")) == 0
    with pytest.raises(ElementNotFound):
        windows.find_window("name:Calculator")
    assert windows.find_window("name:Calculator", raise_error=False) is None
    try:
        windows.desktop().windows_run("calc.exe")
        assert windows.find_window("name:Calculator") is not None

        windows.desktop().windows_run("calc.exe")

        def find_2_calculators():
            return len(windows.find_windows("name:Calculator")) == 2

        wait_for_condition(find_2_calculators)
    finally:
        windows.desktop().close_windows("name:Calculator")


def test_print(tk_process, str_regression):
    import re
    from io import StringIO

    from robocorp.windows import find_window

    window = find_window('name:"Tkinter Elements Showcase"')

    s = StringIO()
    window.find("path:1").print_tree(stream=s)

    v = s.getvalue()
    pattern = r"handle:[^)]+\)"

    result = re.sub(pattern, "handle:XXX", v).replace("\r\n", "\n").replace("\r", "\n")
    str_regression.check(result)


def test_find(tk_process):
    from robocorp.windows import find_window
    from robocorp.windows._control_element import ControlElement
    from robocorp.windows._errors import ElementNotFound

    window = find_window('name:"Tkinter Elements Showcase"')

    path_1_5 = window.find("path:1|5")
    assert path_1_5.is_same_as(
        window.find('desktop > name:"Tkinter Elements Showcase" depth:1 > path:1|5')
    )

    # The path matches, but the class didn't match!
    with pytest.raises(ElementNotFound):
        window.find("class:Invalid path:1|5", timeout=1)
    assert window.find("class:Button path:1|5", timeout=1) is not None
    assert window.find("class:Invalid path:1|5", timeout=1, raise_error=False) is None

    all_buttons = window.find_many(
        "class:Button", search_depth=8, search_strategy="all"
    )

    # Check find with depth.
    by_depth: Dict[int, List[ControlElement]] = {}
    for bt in all_buttons:
        depth = bt.location_info.depth
        assert depth is not None
        by_depth.setdefault(depth, []).append(bt)

    for depth, bts in by_depth.items():
        at_depth = window.find_many(
            f"class:Button depth:{depth}", search_strategy="all"
        )

        assert len(bts) == len(
            at_depth
        ), f"Error. Did not find expected items at depth: {depth}"

        for expect_bt in bts:
            found = False
            for bt in at_depth:
                if bt.is_same_as(expect_bt):
                    found = True

            assert found

    for depth, bts in by_depth.items():
        bts_with_same_parent = []
        use_parent = None
        for i, bt in enumerate(bts):
            if i == 0:
                continue
            prev = bts[i - 1]

            if bt.get_parent().is_same_as(prev.get_parent()):  # type: ignore
                bts_with_same_parent.append(bt)
                bts_with_same_parent.append(prev)
                use_parent = prev.get_parent()
                break

        if use_parent is not None:
            check_bts = []
            for bt in bts:
                if bt.get_parent().is_same_as(use_parent):  # type: ignore
                    check_bts.append(bt)

            at_depth = use_parent.find_many("class:Button depth:1")  # type: ignore
            assert len(check_bts) == len(
                at_depth
            ), "Error. Did not find expected items at depth: 1"

            for expect_bt in check_bts:
                found = False
                for bt in at_depth:
                    if bt.is_same_as(expect_bt):
                        found = True

                assert found, f"Did not find expected.\n{check_bts}\n{at_depth}"


def test_find_by_executable(notepad_window):
    from robocorp import windows

    notepad_exe_win = windows.find_window("executable:Notepad.exe")
    print(f"Notepad window process ID: {notepad_exe_win.pid}")
    assert notepad_exe_win.is_same_as(notepad_window)
    assert notepad_exe_win.close_window(use_close_button=True) is True
