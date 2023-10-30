from robocorp.tasks import task


@task
def check_browser_install():
    """
    The actual install is mocked. What the test_playwright_browser_install does
    is checking if the log output is what we expect.
    """
    from robocorp.browser import _engines
    from robocorp.browser._engines import BrowserEngine, install_browser

    original_build_command_line = _engines._build_install_command_line

    def mock_func(engine, force):
        original_cmd = original_build_command_line(engine, force)
        assert original_cmd[1:] == ["-m", "playwright", "install", "--force", "chrome"]

        return [
            "python",
            "-c",
            """
import time

for i in range(13):
    print(f'Output: {i}')
    time.sleep(1)
    
# Emulate failure
import sys
sys.exit(1)
""",
        ]

    _engines._build_install_command_line = mock_func

    try:
        install_browser(BrowserEngine.CHROME, force=True, interactive=False)
    finally:
        _engines._build_install_command_line = original_build_command_line
