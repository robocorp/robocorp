# ruff: noqa
# Type not available on Mac/Linux.

from ._config import IS_WINDOWS

if IS_WINDOWS:
    from _ctypes import COMError  # type:ignore
else:

    class COMError(Exception):  # type:ignore
        pass
