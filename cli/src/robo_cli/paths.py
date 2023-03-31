import os
import platform
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(os.getcwd()).absolute()


@lru_cache
def resources_path() -> Path:
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # Destination directory for resources defined in robotd.spec
        return Path(sys._MEIPASS).absolute()  # type: ignore
    except AttributeError:
        # Development-time location is repository root
        return Path(__file__).absolute().parent.parent.parent / "resources"


@lru_cache
def home_path() -> Path:
    if platform.system() == "Windows":
        return Path.home() / "AppData" / "Local" / "robocorp" / "robo"
    else:
        return Path.home() / ".robocorp" / "robo"
