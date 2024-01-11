import warnings

from robocorp.http._http import download

__version__ = "0.4.1"
__all__ = [
    "download",
]

warnings.warn(
    "This library is DEPRECATED, please use `requests` instead! "
    "(https://github.com/robocorp/robocorp/blob/master/docs/3rd_party/"
    "requests/README.md)",
    DeprecationWarning,
    stacklevel=2,
)
