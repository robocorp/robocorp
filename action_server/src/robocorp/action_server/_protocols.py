from enum import Enum
from typing import Any, Generic, Optional, TypedDict, TypeVar

T = TypeVar("T")


class Sentinel(Enum):
    SENTINEL = 0


class ActionResultDict(TypedDict):
    success: bool
    message: Optional[
        str
    ]  # if success == False, this can be some message to show to the user
    result: Any


class ActionResult(Generic[T]):
    success: bool
    message: Optional[
        str
    ]  # if success == False, this can be some message to show to the user
    result: Optional[T]

    def __init__(
        self, success: bool, message: Optional[str] = None, result: Optional[T] = None
    ):
        self.success = success
        self.message = message
        self.result = result

    def as_dict(self) -> ActionResultDict:
        return {"success": self.success, "message": self.message, "result": self.result}

    def __str__(self):
        return (
            f"ActionResult(success={self.success!r}, message={self.message!r}, "
            f"result={self.result!r})"
        )

    __repr__ = __str__


class RCCActionResult(ActionResult[str]):
    # A string-representation of the command line.
    command_line: str

    def __init__(
        self,
        command_line: str,
        success: bool,
        message: Optional[str] = None,
        result: Optional[str] = None,
    ):
        ActionResult.__init__(self, success, message, result)
        self.command_line = command_line


def check_implements(x: T) -> T:
    """
    Helper to check if a class implements some protocol.

    :important: It must be the last method in a class due to
                https://github.com/python/mypy/issues/9266

        Example:

    def __typecheckself__(self) -> None:
        _: IExpectedProtocol = check_implements(self)

    Mypy should complain if `self` is not implementing the IExpectedProtocol.
    """
    return x
