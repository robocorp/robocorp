import os
import urllib.parse as urlparse
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


def url_join(*parts: str) -> Optional[str]:
    """Join parts of URL and handle missing/duplicate slashes."""
    if not parts:
        return None

    url = parts[0].rstrip("/") + "/"
    for part in parts[1:]:
        url = urlparse.urljoin(url, part.strip("/") + "/")
    return url
