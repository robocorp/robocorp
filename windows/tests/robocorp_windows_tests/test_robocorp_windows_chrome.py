def test_multiple_interactions():
    import os
    from pathlib import Path

    from robocorp import windows

    desktop = windows.desktop()
    desktop.windows_run("chrome.exe")
    w = desktop.wait_for_active_window("executable:chrome.exe", timeout=20)

    sample_html = os.path.join(os.path.dirname(__file__), "sample.html")
    assert os.path.exists(sample_html)
    url = Path(sample_html).as_uri()

    address_bar = w.find('control:EditControl name:"Address and search bar"')

    address_bar.send_keys("{Alt}d", wait_time=0.2, send_enter=False)
    address_bar.send_keys(url, wait_time=3, send_enter=True)

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
