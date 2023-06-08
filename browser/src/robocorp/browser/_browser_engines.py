import os
import platform
import subprocess
import sys
from enum import Enum
from functools import lru_cache
from pathlib import Path


class InstallError(RuntimeError):
    """Error encountered during browser install"""


class BrowserEngine(str, Enum):
    CHROMIUM = "chromium"
    CHROME = "chrome"
    CHROME_BETA = "chrome-beta"
    MSEDGE = "msedge"
    MSEDGE_BETA = "msedge-beta"
    MSEDGE_DEV = "msedge-dev"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


# Map of BrowserEngine to Playwright driver & channel
ENGINE_TO_ARGS = {
    BrowserEngine.CHROMIUM: ("chromium", None),
    BrowserEngine.CHROME: ("chromium", "chrome"),
    BrowserEngine.CHROME_BETA: ("chromium", "chrome-beta"),
    BrowserEngine.MSEDGE: ("chromium", "msedge"),
    BrowserEngine.MSEDGE_BETA: ("chromium", "msedge-beta"),
    BrowserEngine.MSEDGE_DEV: ("chromium", "msedge-dev"),
    BrowserEngine.FIREFOX: ("firefox", None),
    BrowserEngine.WEBKIT: ("webkit", None),
}


@lru_cache
def browsers_path() -> Path:
    if platform.system() == "Windows":
        return Path.home() / "AppData" / "Local" / "robocorp" / "playwright"
    else:
        return Path.home() / ".robocorp" / "playwright"


def install_browser(engine: BrowserEngine, force=False, interactive=False):
    cmd = [sys.executable, "-m", "playwright", "install"]
    if force:
        cmd.append("--force")

    name = BrowserEngine(engine).value
    cmd.append(name)

    env = dict(os.environ)
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_path())

    result = subprocess.run(
        cmd,
        capture_output=not interactive,
        start_new_session=not interactive,
        text=True,
        env=env,
    )

    if result.returncode != 0:
        if not interactive:
            raise InstallError(f"Failed to install {name}:\n{result.stdout}")
        else:
            raise InstallError(f"Failed to install {name}")
