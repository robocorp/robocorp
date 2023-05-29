import platform
import shutil
from pathlib import Path
from typing import Literal, Optional, Union, cast

Engine = Literal["chrome"]


def to_engine(value: Union[str, Engine]) -> Engine:
    if value not in ["chrome"]:
        raise ValueError(f"Invalid browser engine: {value}")

    return cast(Engine, value)


def get_executable_path(browser: Engine) -> str:
    system = platform.system()

    if system == "Darwin":
        path = _get_executable_darwin(browser)
    elif system == "Linux":
        path = _get_executable_linux(browser)
    elif system == "Windows":
        path = _get_executable_windows(browser)
    else:
        raise ValueError(f"Unsupported platform: {system}")

    if path is None:
        raise RuntimeError(f"Browser executable not found: {browser}")

    return path


def _get_executable_darwin(browser: Engine) -> Optional[str]:
    if browser == "chrome":
        options = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    for option in options:
        if Path(option).exists():
            return option

    return None


def _get_executable_linux(browser: Engine) -> Optional[str]:
    if browser == "chrome":
        options = [
            "google-chrome",
            "chromium-browser",
            "chromium",
        ]
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    for option in options:
        if (path := shutil.which(option)) is not None:
            return path

    return None


def _get_executable_windows(browser: Engine) -> Optional[str]:
    if browser == "chrome":
        options = [
            "chrome",
            "chrome.exe",
            "chromium",
            "chromium.exe",
        ]
    else:
        raise ValueError(f"Unsupported browser: {browser}")

    for option in options:
        if (path := shutil.which(option)) is not None:
            return path

    return None
