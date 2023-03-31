import platform

from playwright.sync_api import sync_playwright as _sync_playwright

EXECUTABLE_PATHS = {
    "chromium": {
        "Linux": "/usr/bin/chromium-browser",
        "Windows": "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "Darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    },
    "firefox": {
        "Linux": "/usr/bin/firefox",
        "Windows": "C:\\Program Files\\Mozilla Firefox\\firefox.exe",
        "Darwin": "/Applications/Firefox.app/Contents/MacOS/firefox",
    },
}


def open_available_browser(browser="chromium"):
    system = platform.system()
    with _sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=EXECUTABLE_PATHS[browser][system], headless=False
        )
        context = browser.new_context()
        page = context.new_page()
        page.goto("http://rpachallenge.com/")
        return page


def non_context_managery_playwright():
    # Based on https://peps.python.org/pep-0343/#specification-the-with-statement
    mgr = _sync_playwright()
    exit = type(mgr).__exit__  # Not calling it yet
    value = type(mgr).__enter__(mgr)
    exc = True
    try:
        try:
            VAR = value  # Only if "as VAR" is present
            BLOCK
        except:
            # The exceptional case is handled here
            exc = False
            if not exit(mgr, *sys.exc_info()):
                raise
            # The exception is swallowed if exit() returns true
    finally:
        # The normal and non-local-goto cases are handled here
        if exc:
            exit(mgr, None, None, None)


if __name__ == "__main__":
    open_available_browser()

#     Open Available Browser    http://rpachallenge.com/


# Close All Browsers


#  Click Button    Start


# Input Text    alias:First Name    ${person}[First Name]


# Capture Element Screenshot    alias:Congratulations
