from typing import Optional, Type

from ._types import ExceptionType


class EmptyQueue(IndexError):
    """Raised when trying to load an input item and none available."""


class _BaseException(RuntimeError):
    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        self.message = message
        self.code = code


class BusinessException(_BaseException):
    """
    An exception that can be raised to release an input work item with
    a BUSINESS exception type.
    """


class ApplicationException(_BaseException):
    """
    An exception that can be raised to release an input work item with
    a BUSINESS exception type.
    """


def to_exception_type(exc_type: Type[BaseException]) -> ExceptionType:
    if exc_type is BusinessException:
        return ExceptionType.BUSINESS
    elif exc_type is ApplicationException:
        return ExceptionType.APPLICATION
    else:
        return ExceptionType.APPLICATION
