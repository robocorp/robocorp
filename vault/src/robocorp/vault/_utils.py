import importlib
import os
from pathlib import Path
from typing import Any, Optional

# Sentinel value for undefined argument
UNDEFINED = object()


def required_env(name: str, default: Any = UNDEFINED) -> str:
    """Load required environment variable.

    Args:
        name: Name of environment variable
        default: Value to use if variable is undefined.
                    If not given and variable is undefined, raises KeyError.

    """
    val = os.getenv(name, default)
    if val is UNDEFINED:
        raise KeyError(f"Missing required environment variable: {name}")
    return val


def import_by_name(name: str, caller: Optional[str] = None) -> Any:
    """Import module (or attribute) by name.

    Args:
        name: Import path, e.g. RPA.Robocorp.WorkItems.RobocorpAdapter
        caller: Caller file name

    """
    name = str(name)

    # Attempt import as path module
    try:
        return importlib.import_module(name)
    except ImportError:
        pass

    # Attempt import from calling file
    if caller is not None:
        try:
            module = importlib.import_module(caller)
            return getattr(module, name)
        except AttributeError:
            pass

    # Attempt import as path to attribute inside module
    if "." in name:
        try:
            path, attr = name.rsplit(".", 1)
            module = importlib.import_module(path)
            return getattr(module, attr)
        except (AttributeError, ImportError):
            pass

    raise ValueError(f"No module/attribute with name: {name}")


def resolve_path(path: str) -> Path:
    """Resolve a string-based path, and replace variables."""
    return Path(path).expanduser().resolve()


def url_join(*parts):
    """Join parts of URL and handle missing/duplicate slashes."""
    return "/".join(str(part).strip("/") for part in parts)
