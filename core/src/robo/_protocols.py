from pathlib import Path
from typing import TypeVar
import typing


T = TypeVar("T")
Y = TypeVar("Y", covariant=True)


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


class Status:
    NOT_RUN = "NOT RUN"
    PASS = "PASS"
    ERROR = "ERROR"


class ITask(typing.Protocol):
    package_name: str
    filename: str
    method: typing.Callable

    status: str
    message: str

    @property
    def name(self) -> str:
        pass

    @property
    def lineno(self) -> int:
        pass

    def run(self) -> None:
        pass


class ICallback(typing.Protocol):
    """
    Note: the actual __call__ must be defined in a subclass protocol.
    """

    def register(self, callback):
        pass

    def unregister(self, callback):
        pass


class IOnTaskFuncFoundCallback(ICallback, typing.Protocol):
    def __call__(self, task: ITask):
        pass


class IBeforeCollectTasksCallback(ICallback, typing.Protocol):
    def __call__(self, path: Path, task_name: str):
        pass


class IBeforeTaskRunCallback(ICallback, typing.Protocol):
    def __call__(self, task: ITask):
        pass


class IAfterTaskRunCallback(ICallback, typing.Protocol):
    def __call__(self, task: ITask):
        pass
