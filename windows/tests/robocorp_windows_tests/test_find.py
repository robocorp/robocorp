import pytest


def test_find_windows():
    from robocorp_windows_tests.fixtures import wait_for_condition

    from robocorp import windows

    windows.desktop().close_windows("name:Calculator")
    assert len(windows.find_windows("name:Calculator")) == 0
    try:
        windows.desktop().windows_run("calc.exe")
        assert windows.find_window("name:Calculator") is not None

        windows.desktop().windows_run("calc.exe")

        def find_2_calculators():
            return len(windows.find_windows("name:Calculator")) == 2

        wait_for_condition(find_2_calculators)
    finally:
        windows.desktop().close_windows("name:Calculator")


def test_find_(tk_process):
    from robocorp.windows import find_window
    from robocorp.windows._errors import ElementNotFound

    window = find_window('name:"Tkinter Elements Showcase"')

    window.find("path:1|5")

    # The path matches, but the class didn't match!
    with pytest.raises(ElementNotFound):
        window.find("class:Invalid path:1|5", timeout=1)
    assert window.find("class:Button path:1|5", timeout=1) is not None
