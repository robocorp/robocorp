import inspect
import typing
from contextlib import contextmanager
from types import ModuleType
from typing import Any, Dict, List, Literal, Optional, Tuple, get_type_hints

from robocorp.log import ConsoleMessageKind, console_message
from robocorp.log.protocols import OptExcInfo

from robocorp.tasks._constants import SUPPORTED_TYPES_IN_SCHEMA
from robocorp.tasks._protocols import IContext, ITask, Status


def _build_properties(
    method_name: str,
    name_for_title: str,
    param_type: Any,
    description: str,
    kind: Literal["parameter", "return"],
) -> Dict[str, Any]:
    if not param_type:
        param_type_clsname = "string"
    else:
        if param_type not in SUPPORTED_TYPES_IN_SCHEMA:
            param_type_clsname = f"Error. The {kind} type '{param_type.__name__}' in '{method_name}' is not supported. Supported {kind} types: str, int, float, bool."
        else:
            if param_type == str:
                param_type_clsname = "string"
            elif param_type == int:
                param_type_clsname = "integer"
            elif param_type == float:
                param_type_clsname = "number"
            elif param_type == bool:
                param_type_clsname = "boolean"

    properties = {
        "type": param_type_clsname,
        "description": description,
    }

    if name_for_title:
        properties["title"] = name_for_title.replace("_", " ").title()
    return properties


class Task:
    def __init__(
        self,
        module: ModuleType,
        method: typing.Callable,
        options: Optional[Dict] = None,
    ):
        self.module_name = module.__name__
        self.filename = module.__file__ or "<filename unavailable>"
        self.method = method
        self.message = ""
        self.exc_info: Optional[OptExcInfo] = None
        self._status = Status.NOT_RUN
        self.result = None
        self.options = options or None

    @property
    def name(self):
        return self.method.__code__.co_name

    @property
    def lineno(self):
        return self.method.__code__.co_firstlineno

    def run(self, *args, **kwargs):
        sig = inspect.signature(self.method)
        try:
            sig.bind(*args, **kwargs)
        except Exception as e:
            raise RuntimeError(
                f"It's not possible to call the task: '{self.name}' because the passed arguments don't match the task signature.\nError: {e}"
            )
        return self.method(*args, **kwargs)

    @property
    def input_schema(self) -> dict[str, Any]:
        import docstring_parser

        sig = inspect.signature(self.method)
        method_name = self.method.__code__.co_name
        type_hints = get_type_hints(self.method)

        param_name_to_description: Dict[str, str] = {}

        doc = getattr(self.method, "__doc__", "")
        if doc:
            contents = docstring_parser.parse(doc)
            for docparam in contents.params:
                if docparam.description:
                    param_name_to_description[docparam.arg_name] = docparam.description

        properties: Dict[str, Any] = {}
        required: List[str] = []

        schema = {
            "additionalProperties": False,
            "properties": properties,
            "type": "object",
        }

        for param in sig.parameters.values():
            param_type = type_hints.get(param.name)
            description = param_name_to_description.get(param.name, "")
            param_properties = _build_properties(
                method_name, param.name, param_type, description, "parameter"
            )
            properties[param.name] = param_properties

            if param.default is inspect.Parameter.empty:
                required.append(param.name)
            else:
                param_properties["default"] = str(param.default)

        if required:
            schema["required"] = required

        return schema

    @property
    def output_schema(self) -> dict[str, Any]:
        import docstring_parser

        method_name = self.method.__code__.co_name
        type_hints = get_type_hints(self.method)

        doc = getattr(self.method, "__doc__", "")
        description = ""
        if doc:
            contents = docstring_parser.parse(doc)
            returns = contents.returns
            if returns and returns.description:
                description = returns.description

        schema = _build_properties(
            method_name, "", type_hints.get("return"), description, "return"
        )
        return schema

        # We could use pydantic, but then adding the info from
        # the docstring is harder...
        # from pydantic.json_schema import GenerateJsonSchema
        # from pydantic.validate_call import validate_call
        #
        # m = validate_call(validate_return=True)(self.method)
        # schema = m.__return_pydantic_core_schema__
        # return GenerateJsonSchema().generate(schema) or {}

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, value: Status):
        self._status = Status(value)

    @property
    def failed(self):
        return self._status == Status.FAIL

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
        if task.status == Status.FAIL:
            status_kind = self.KIND_ERROR

        show = self.show
        show(f"{task.name}", end="", kind=self.KIND_TASK_NAME)
        show(" status: ", end="")
        show(f"{task.status.value}", kind=status_kind)
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
