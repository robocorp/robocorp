import sys
from pathlib import Path


def resources_path() -> Path:
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # Destination directory for resources defined in robotd.spec
        return Path(sys._MEIPASS).resolve()
    except AttributeError:
        # Development-time location is repository root
        return Path(__file__).resolve().parent.parent.parent / "resources"
