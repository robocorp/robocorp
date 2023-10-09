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
