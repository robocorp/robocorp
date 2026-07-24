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

    # In GitHub Actions on a fresh install Chrome asks to sign in. We have to
    # decline. The exact dialog/button wording has changed across Chrome
    # versions (e.g. "Don't sign in" -> "Stay signed out"), so match on the
    # stable button id first and fall back to the older text pattern. On
    # machines where Chrome is already signed in this prompt never appears,
    # so use a short timeout + raise_error=False here instead of the global
    # 10s default - otherwise each of these best-effort lookups blocks for
    # the full default timeout before giving up.
    try:
        app = windows.find_window("regex:.*Google Chrome", timeout=5)
    except windows.ElementNotFound:
        app = None

    if app is not None:
        decline_button = app.find(
            "(id:declineSignInButton or regex:Don.*sign.*in) and "
            'control:"ButtonControl"',
            search_depth=12,
            timeout=2,
            raise_error=False,
        )
        if decline_button is not None:
            decline_button.click()

        skip_button = app.find(
            'control:"ButtonControl" and name:Skip',
            search_depth=12,
            timeout=2,
            raise_error=False,
        )
        if skip_button is not None:
            skip_button.click()

    # The tab title may or may not carry a "New Tab" prefix depending on the
    # Chrome first-run state, so match either form. Note: the locator DSL
    # itself uses "(" / ")" for grouping, so a regex value can't contain
    # literal parens here. Give it a longer timeout since the title can take
    # a moment to settle after a fresh install.
    w = windows.find_window("regex:.*Google Chrome", wait_time=0.5, timeout=10)
    w.send_keys("{Alt}d", wait_time=0.2, send_enter=False)
    w.send_keys(url, wait_time=3, send_enter=True)

    # Test select
    combo = w.find("control:ComboBoxControl id:cars", search_depth=12)
    combo.select("Audi")
    assert combo.get_value() == "Audi"

    # Test get_value/set_value
    text_control = w.find("id:fname", search_depth=12)
    assert text_control.get_value() == ""
    text_control.set_value("22")
    assert text_control.get_value() == "22"

    # Test drag and drop
    div_header_item = w.find("id:mydiv > id:mydivheader", search_depth=12)
    move_item = w.find("id:mydiv > control:TextControl name:Move", search_depth=12)

    original_top = div_header_item.top
    desktop.drag_and_drop(div_header_item, move_item)
    div_header_item.update_geometry()
    assert original_top < div_header_item.top

    # Close the Chrome opened in the test.
    w.send_keys("{Ctrl}w")
