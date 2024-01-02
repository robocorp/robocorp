import typing
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from types import TracebackType
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    Optional,
    Sequence,
    Set,
    TypeVar,
    Union,
)

ExcInfo = tuple[type[BaseException], BaseException, TracebackType]
OptExcInfo = Union[ExcInfo, tuple[None, None, None]]


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


class Status(str, Enum):
    """Task state"""

    NOT_RUN = "NOT_RUN"
    PASS = "PASS"
    FAIL = "FAIL"


class ITask(typing.Protocol):
    module_name: str
    filename: str
    method: typing.Callable

    status: Status
    message: str
    exc_info: Optional[OptExcInfo]

    # If the task completed successfully, this will be
    # the value returned by the task.
    result: Any

    options: Optional[Dict]

    @property
    def input_schema(self) -> Dict[str, Any]:
        pass

    @property
    def output_schema(self) -> Dict[str, Any]:
        pass

    @property
    def name(self) -> str:
        pass

    @property
    def lineno(self) -> int:
        pass

    def run(self) -> Any:
        pass

    @property
    def failed(self) -> bool:
        """
        Returns true if the task failed.
        (in which case usually exc_info is not None).
        """


class IContext(typing.Protocol):
    def show(
        self, msg: str, end: str = "", kind: str = "", flush: Optional[bool] = None
    ):
        pass

    def show_error(self, msg: str, flush: Optional[bool] = None):
        pass

    @contextmanager
    def register_lifecycle_prints(self) -> Iterator[None]:
        pass


class ICallback(typing.Protocol):
    """
    Note: the actual __call__ must be defined in a subclass protocol.
    """

    def register(self, callback):
        pass

    def unregister(self, callback):
        pass


class IAutoUnregisterContextManager(typing.Protocol):
    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class IOnTaskFuncFoundCallback(ICallback, typing.Protocol):
    def __call__(self, func: Callable, *args, **kwargs):
        pass

    def register(self, callback: Callable) -> IAutoUnregisterContextManager:
        pass

    def unregister(self, callback: Callable) -> None:
        pass


class IBeforeCollectTasksCallback(ICallback, typing.Protocol):
    def __call__(self, path: Path, task_names: Set[str]):
        pass

    def register(
        self, callback: Callable[[Path, Set[str]], Any]
    ) -> IAutoUnregisterContextManager:
        pass

    def unregister(self, callback: Callable[[Path, Set[str]], Any]) -> None:
        pass


ITaskCallback = Callable[[ITask], Any]
ITasksCallback = Callable[[Sequence[ITask]], Any]


class IBeforeTaskRunCallback(ICallback, typing.Protocol):
    def __call__(self, task: ITask):
        pass

    def register(self, callback: ITaskCallback) -> IAutoUnregisterContextManager:
        pass

    def unregister(self, callback: ITaskCallback) -> None:
        pass


class IBeforeAllTasksRunCallback(ICallback, typing.Protocol):
    def __call__(self, tasks: Sequence[ITask]):
        pass

    def register(self, callback: ITasksCallback) -> IAutoUnregisterContextManager:
        pass

    def unregister(self, callback: Callable[[Sequence[ITask]], Any]) -> None:
        pass


class IAfterAllTasksRunCallback(ICallback, typing.Protocol):
    def __call__(self, tasks: Sequence[ITask]):
        pass

    def register(self, callback: ITasksCallback) -> IAutoUnregisterContextManager:
        pass

    def unregister(self, callback: ITasksCallback) -> None:
        pass


class IAfterTaskRunCallback(ICallback, typing.Protocol):
    def __call__(self, task: ITask):
        pass

    def register(self, callback: ITaskCallback) -> IAutoUnregisterContextManager:
        pass

    def unregister(self, callback: ITaskCallback) -> None:
        pass
