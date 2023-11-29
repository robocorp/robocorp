from typing import Any, Callable, Sequence

from robocorp.tasks import ITask as _ITask
from robocorp.tasks import Status as _Status

IAction = _ITask
Status = _Status

IActionCallback = Callable[[IAction], Any]
IActionsCallback = Callable[[Sequence[IAction]], Any]
