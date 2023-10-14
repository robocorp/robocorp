def _start_explorer_at_folder(folder: str):
    from robocorp import windows
    from robocorp.windows import ElementNotFound

    desktop = windows.desktop()
    desktop.send_keys("{win}e")
    try:
        explorer = desktop.wait_for_active_window("name:Home", timeout=2)
    except ElementNotFound:
        explorer = desktop.wait_for_active_window('name:"File Explorer"')
    explorer.send_keys("{alt}d")
    explorer.send_keys(folder, send_enter=True)
    return explorer


def test_copy_with_explorer(tmpdir):
    import os
    from pathlib import Path

    from robocorp_windows_tests.fixtures import wait_for_condition

    from robocorp import windows
    from robocorp.windows._errors import ElementNotFound

    folder_a = tmpdir.join("folderA")
    folder_a.mkdir()
    folder_b = tmpdir.join("folderB")
    folder_b.mkdir()

    dummy_src = Path(str(folder_a.join("dummy_file.txt")))
    dummy_src.write_text("Dummy")

    dummy_to_create = Path(str(folder_b.join("dummy_file.txt")))

    desktop = windows.desktop()
    explorer1 = _start_explorer_at_folder(str(folder_a))
    explorer1.set_window_pos(0, 0, desktop.width / 2, desktop.height)

    explorer2 = _start_explorer_at_folder(str(folder_b))
    explorer2.set_window_pos(desktop.width / 2, 0, desktop.width / 2, desktop.height)

    # copying a file, dummy_file.txt, from source (File Explorer) window
    # into a target (File Explorer) Window
    try:
        report_html = explorer1.find("name:dummy_file.txt type:ListItem", timeout=1)
    except ElementNotFound:
        try:
            report_html = explorer1.find(
                "name:dummy_file.txt control:ListItemControl", timeout=1
            )
        except ElementNotFound:
            report_html = explorer1.find(
                "name:dummy_file control:ListItemControl", timeout=1
            )
    items_view = explorer2.find('name:"Items View"')
    desktop.drag_and_drop(report_html, items_view, hold_ctrl=True)

    wait_for_condition(dummy_to_create.exists)

    os.remove(dummy_to_create)

    wait_for_condition(lambda: not dummy_to_create.exists())
    explorer2.send_keys("{F5}")

    # Now, move instead of copy
    desktop.drag_and_drop(report_html, items_view, hold_ctrl=False)
    explorer1.send_keys("{F5}")
    explorer2.send_keys("{F5}")
    wait_for_condition(lambda: not dummy_src.exists())
    wait_for_condition(lambda: dummy_to_create.exists())

    explorer1.click("control:ButtonControl name:Close")
    wait_for_condition(explorer1.is_disposed)

    explorer2.click("control:ButtonControl name:Close")
    wait_for_condition(explorer2.is_disposed)
