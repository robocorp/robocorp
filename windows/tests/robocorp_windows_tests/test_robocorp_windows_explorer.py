def _start_explorer_at_folder(folder: str):
    from robocorp import windows

    desktop = windows.desktop()
    desktop.send_keys("{win}e")
    explorer = desktop.wait_for_active_window(
        'name:Home or name:"File Explorer"', timeout=2
    )
    explorer.send_keys("{alt}d")
    # TODO: provide API related to checking focus.
    # desktop.wait_for_focused_control('class:TextBox name:"Address Bar"')
    explorer.send_keys(folder, send_enter=True)
    return explorer


def test_copy_with_explorer(tmpdir):
    import os
    from pathlib import Path

    from robocorp_windows_tests.fixtures import wait_for_condition

    from robocorp import windows

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
    report_html = explorer1.find(
        "(name:dummy_file.txt type:ListItem) or "
        "(name:dummy_file.txt control:ListItemControl) or "
        "(name:dummy_file control:ListItemControl)"
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
