import logging
from typing import Callable, Optional, Union, cast

from robocorp.tasks import get_current_task, task_cache

from ._context import Context
from ._exceptions import (
    ApplicationException,
    BusinessException,
    EmptyQueue,
    to_exception_type,
)
from ._types import ExceptionType, JSONType, State
from ._workitem import Input, Output

__version__ = "1.0.0"
version_info = [int(x) for x in __version__.split(".")]

LOGGER = logging.getLogger(__name__)


@task_cache
def __ctx():
    """Create a shared context for the task execution.

    Automatically loads the first input item, as one is always automatically
    reserved from the queue by Control Room.

    After the task finishes, logs a warning if any output work items are
    unsaved, and releases the current input if the task failed with an
    exception.
    """
    ctx = Context()
    ctx.reserve_input()

    yield ctx

    for item in ctx.outputs:
        if not item.saved:
            LOGGER.warning("%s has unsaved changes that will be discarded", item)

    current = ctx.current_input
    if current is None or current.released:
        return

    task = get_current_task()
    if not task:
        return

    if task.exc_info is not None:
        exc_type, exc_value, _ = task.exc_info

        exception_type = to_exception_type(exc_type)
        code = getattr(exc_value, "code", None)
        message = getattr(exc_value, "message", str(exc_value))

        current.fail(exception_type, code, message)


# Workaround for @task_cache handling the generator
_ctx = cast(Callable[[], Context], __ctx)


class Inputs:
    """Inputs represents the input queue of work items.

    It can be used to reserve and release items from the queue,
    and iterate over them.

    Example:
        Multiple items can behandled by iterating over this class::

            for item in inputs:
                handle_item(item.payload)
    """

    def __iter__(self):
        if self.current and not self.current.released:
            with self.current as item:
                yield item

        while True:
            try:
                with self.reserve() as item:
                    yield item
            except EmptyQueue:
                break

    @property
    def current(self) -> Optional[Input]:
        """The current reserved input item."""
        return _ctx().current_input

    @property
    def released(self) -> list[Input]:
        """A list of inputs reserved and released during the lifetime
        of the library.
        """
        return [item for item in _ctx().inputs if item.released]

    def reserve(self) -> Input:
        """Reserve a new input work item.

        There can only be one item reserved at a time.

        Returns:
            Input work item

        Raises:
            RuntimeError: An input work item is already reserved
            workitems.EmptyQueue: There are no further items in the queue
        """
        return _ctx().reserve_input()


class Outputs:
    """Outputs represents the output queue of work items.

    It can be used to create outputs and inspect the items created during the execution.

    Example:
        The class can be used to create outputs::

            outputs.create({"key": "value"})
    """

    def __len__(self):
        return len(_ctx().outputs)

    def __getitem__(self, key):
        return _ctx().outputs[key]

    def __iter__(self):
        return iter(_ctx().outputs)

    def __reversed__(self):
        return reversed(_ctx().outputs)

    @property
    def last(self) -> Optional[Output]:
        """The most recently created output work item, or `None`."""
        if not _ctx().outputs:
            return None

        return _ctx().outputs[-1]

    def create(
        self,
        payload: Optional[JSONType] = None,
        files: Optional[Union[str, list[str]]] = None,
        save: bool = True,
    ) -> Output:
        """Create a new output work item, which can have both a JSON
        payload and attached files.

        Creating an output item requires an input to be currently reserved.

        Args:
            payload: JSON serializable data (dict, list, scalar, etc.)
            files: List of paths to files or glob pattern
            save: Immediately save item after creation

        Raises:
            RuntimeError: No input work item reserved
        """
        item = _ctx().create_output()

        if payload is not None:
            item.payload = payload

        if files is not None:
            if isinstance(files, str):
                item.add_files(pattern=files)
            else:
                for path in files:
                    item.add_file(path=path)

        if save:
            item.save()

        return item


inputs = Inputs()
outputs = Outputs()

__all__ = [
    "EmptyQueue",
    "BusinessException",
    "ApplicationException",
    "State",
    "ExceptionType",
    "Input",
    "Output",
    "inputs",
    "outputs",
]
