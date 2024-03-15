import typing
from typing import Any, Callable, Sequence

from robocorp.tasks import ITask as _ITask
from robocorp.tasks import Status as _Status


class IAction(_ITask, typing.Protocol):
    pass


Status = _Status

IActionCallback = Callable[[IAction], Any]
IActionsCallback = Callable[[Sequence[IAction]], Any]
