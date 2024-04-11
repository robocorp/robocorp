def test_multiple_interactions():
    try:
        _check_multiple_interactions()
    except BaseException:
        # We're not using robocorp.tasks to run, so, we don't have
        # screenshots automatically.
        from robocorp.windows import desktop

        desktop().log_screenshot()
        raise


def _check_multiple_interactions():
    import os
    from pathlib import Path

    from robocorp import windows

    desktop = windows.desktop()
    desktop.windows_run("chrome.exe")
    desktop.wait_for_active_window("executable:chrome.exe", timeout=20)

    sample_html = os.path.join(os.path.dirname(__file__), "sample.html")
    assert os.path.exists(sample_html)
    url = Path(sample_html).as_uri()

    # In GitHub Actions on a fresh install Chrome asks to sign in.
    # We have to decline
    try:
        app = windows.find_window("regex:.*Sign in to Chrome", timeout=5)
        app.find('control:"ButtonControl" and name:"Close"').click()
    except windows.ElementNotFound:
        pass  # Ignore if not there.

    w = windows.find_window("regex:.*New Tab - Google Chrome", wait_time=0.5, timeout=5)
    w.send_keys("{Alt}d", wait_time=0.2, send_enter=False)
    w.send_keys(url, wait_time=3, send_enter=True)

    # Test select
    combo = w.find("control:ComboBoxControl id:cars", search_depth=10)
    combo.select("Audi")
    assert combo.get_value() == "Audi"

    # Test get_value/set_value
    text_control = w.find('control:EditControl name:"First name:"', search_depth=9)
    assert text_control.get_value() == ""
    text_control.set_value("22")
    assert text_control.get_value() == "22"

    # Test drag and drop
    div_header_item = w.find("id:mydiv > id:mydivheader")
    move_item = w.find("id:mydiv > control:TextControl name:Move")

    original_top = div_header_item.top
    desktop.drag_and_drop(div_header_item, move_item)
    div_header_item.update_geometry()
    assert original_top < div_header_item.top

    # Close the Chrome opened in the test.
    w.send_keys("{Ctrl}w")
