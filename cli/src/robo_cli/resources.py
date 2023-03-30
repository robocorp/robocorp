import sys
from pathlib import Path
from typing import Union

PathLike = Union[str, Path]


def resource_path(path: PathLike):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # Destination directory for resources defined in robotd.spec
        root = Path(sys._MEIPASS).resolve()
    except AttributeError:
        # Development-time location is repository root
        root = Path(__file__).resolve().parent.parent.parent

    return root / "resources" / path
