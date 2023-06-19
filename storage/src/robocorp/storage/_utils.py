import functools
import os
import urllib.parse as urlparse
from typing import Any, Optional

# Sentinel value for undefined arguments.
UNDEFINED = object()


def required_env(name: str, default: Any = UNDEFINED) -> str:
    """Load required environment variable.

    Args:
        name: Name of the requested environment variable.
        default: Value to return if no such env var is found, otherwise `KeyError` is
            raised.
    """
    val = os.getenv(name, default)
    if val is UNDEFINED:
        raise KeyError(f"Missing required environment variable: {name}")
    return val


class RequiresEnv:
    """Raises a custom error when the required env var isn't available."""

    def __init__(self, error_message):
        self._exception = RuntimeError(error_message)

    @functools.wraps(required_env)
    def __call__(self, *args, **kwargs):
        try:
            return required_env(*args, **kwargs)
        except Exception as exc:
            raise self._exception from exc


def url_join(*parts: str) -> Optional[str]:
    """Join parts of URL and handle missing/duplicate slashes."""
    if not parts:
        return None

    url = ""
    for part in parts:
        url = urlparse.urljoin(url, part.strip("/") + "/")
    return url
