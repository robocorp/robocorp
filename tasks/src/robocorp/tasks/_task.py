import typing
from contextlib import contextmanager
from types import ModuleType
from typing import Any, List, Optional, Tuple

from robocorp.log import ConsoleMessageKind, console_message
from robocorp.log.protocols import OptExcInfo

from robocorp.tasks._protocols import IContext, ITask, Status


class Task:
    def __init__(self, module: ModuleType, method: typing.Callable):
        self.module_name = module.__name__
        self.filename = module.__file__ or "<filename unavailable>"
        self.method = method
        self.status = Status.NOT_RUN
        self.message = ""
        self.exc_info: Optional[OptExcInfo] = None

    @property
    def name(self):
        return self.method.__code__.co_name

    @property
    def lineno(self):
        return self.method.__code__.co_firstlineno

    def run(self, **kwargs: dict[str, Any]) -> Any:
        return self.method(**kwargs)

    @property
    def failed(self):
        return self.status in (Status.ERROR, Status.FAIL)

    def __typecheckself__(self) -> None:
        from robocorp.tasks._protocols import check_implements

        _: ITask = check_implements(self)

    def __str__(self):
        return f"Task({self.name}, status: {self.status})"

    __repr__ = __str__


class _TaskContext:
    _current_task: Optional[ITask] = None


def set_current_task(task: Optional[ITask]):
    _TaskContext._current_task = task


def get_current_task() -> Optional[ITask]:
    return _TaskContext._current_task


class Context:
    # Some regular message (generated by the framework).
    KIND_REGULAR = ConsoleMessageKind.REGULAR

    # Some message which deserves a bit more attention (generated by the framework).
    KIND_IMPORTANT = ConsoleMessageKind.IMPORTANT

    # The task name is being written (generated by the framework).
    KIND_TASK_NAME = ConsoleMessageKind.TASK_NAME

    # Some error message (generated by the framework).
    KIND_ERROR = ConsoleMessageKind.ERROR

    # Some traceback message (generated by the framework).
    KIND_TRACEBACK = ConsoleMessageKind.TRACEBACK

    # Some user message which was being sent to the stdout.
    KIND_STDOUT = ConsoleMessageKind.STDOUT

    # Some user message which was being sent to the stderr.
    KIND_STDERR = ConsoleMessageKind.STDERR

    def __init__(self):
        self._msg_len_target = 80

    def _show_header(self, parts: List[Tuple[str, str]]) -> int:
        """
        Returns:
            The final number of chars used in the full header.
        """
        if not parts:
            self.show("=" * self._msg_len_target)
            return self._msg_len_target

        total_len = sum(len(msg) for (msg, _) in parts)

        # + 2 for the spacing before after the '='.
        diff = self._msg_len_target - (total_len + 2)

        start_sep_chars = 3
        end_sep_chars = 3
        if diff > 0:
            start_sep_chars = int(diff / 2)
            end_sep_chars = diff - start_sep_chars

        final_len = 0
        msg_start = f"{'=' * start_sep_chars} "
        final_len += len(msg_start)
        self.show(msg_start, end="")

        for msg, kind in parts:
            final_len += len(msg)
            self.show(msg, end="", kind=kind)

        msg_end = f" {'=' * end_sep_chars}"
        final_len += len(msg_end)
        self.show(msg_end)

        return final_len

    def show(
        self, msg: str, end: str = "\n", kind=KIND_REGULAR, flush: Optional[bool] = None
    ):
        """
        Shows a message to the user.

        Args:
            msg: The message to be shown.
            end: The end char to be added to the message.
            kind: The kind of the message.
            flush: Whether we should flush after sending the message (if None
                   it's flushed if the end char ends with '\n').
        """
        if end:
            msg = f"{msg}{end}"
        console_message(msg, kind, flush=flush)

    def show_error(self, msg: str, flush: Optional[bool] = None):
        self.show(msg, kind=self.KIND_ERROR, flush=flush)

    def _before_task_run(self, task: ITask):
        self._msg_len_target = 80
        self._msg_len_target = self._show_header(
            [("Running: ", self.KIND_REGULAR), (task.name, self.KIND_TASK_NAME)]
        )

    def _after_task_run(self, task: ITask):
        import traceback

        msg = ""
        if task.message:
            msg = f"\n{task.message}"

        status_kind = self.KIND_REGULAR
        if task.status == Status.ERROR:
            status_kind = self.KIND_ERROR

        show = self.show
        show(f"{task.name}", end="", kind=self.KIND_TASK_NAME)
        show(f" status: ", end="")
        show(f"{task.status}", kind=status_kind)
        if msg:
            show(f"{msg}", kind=status_kind)

            if task.exc_info and task.exc_info[0]:
                self._show_header(
                    [
                        ("Full Traceback (running ", self.KIND_REGULAR),
                        (task.name, self.KIND_TASK_NAME),
                        (")", self.KIND_REGULAR),
                    ]
                )

                self.show(
                    "".join(traceback.format_exception(*task.exc_info)),
                    kind=self.KIND_TRACEBACK,
                )

        self._show_header([])

    @contextmanager
    def register_lifecycle_prints(self):
        from ._hooks import after_task_run, before_task_run

        with before_task_run.register(self._before_task_run), after_task_run.register(
            self._after_task_run
        ):
            yield

    def __typecheckself__(self) -> None:
        from robocorp.tasks._protocols import check_implements

        _: IContext = check_implements(self)
