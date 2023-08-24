from typing import Optional, Type

from ._types import ExceptionType


class EmptyQueue(IndexError):
    """Raised when trying to load an input item and none available."""


class _BaseException(RuntimeError):
    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        self.message = message
        self.code = code

    def __str__(self):
        args = ", ".join(
            f'"{arg}"' for arg in [self.message, self.code] if arg is not None
        )
        return f"{self.__class__.__name__}({args})"


class BusinessException(_BaseException):
    """
    An exception that can be raised to release an input work item with
    a BUSINESS exception type.
    """


class ApplicationException(_BaseException):
    """
    An exception that can be raised to release an input work item with
    an APPLICATION exception type.
    """


def to_exception_type(exc_type: Type[BaseException]) -> ExceptionType:
    if issubclass(exc_type, BusinessException):
        return ExceptionType.BUSINESS
    elif issubclass(exc_type, ApplicationException):
        return ExceptionType.APPLICATION
    else:
        return ExceptionType.APPLICATION
