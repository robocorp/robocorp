from types import TracebackType
from typing import Union, Literal, Protocol, List

ExcInfo = tuple[type[BaseException], BaseException, TracebackType]
OptExcInfo = Union[ExcInfo, tuple[None, None, None]]

LogHTMLStyle = Literal["standalone", "vscode"]


class IReadLines(Protocol):
    def readlines(self) -> List[str]:
        pass


class Status:
    NOT_RUN = "NOT_RUN"  # Initial status for a task which is not run.
    PASS = "PASS"
    ERROR = "ERROR"
    FAIL = "FAIL"
    INFO = "INFO"
    WARN = "WARN"
