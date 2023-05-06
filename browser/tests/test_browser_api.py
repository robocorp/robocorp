def test_browser_api() -> None:
    from robocorp import browser

    page = browser.page
    page.goto("http://robocorp.com")
    for selector in page.query_selector_all(".label"):
        print(selector.text_content())

    new_page = browser.context.new_page()
    new_page.goto("http://somewhere.com")
    new_page.close()
