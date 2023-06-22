from types import TracebackType
from typing import List, Literal, Protocol, Union

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


# 'METHOD': means that we entered a regular method which should be added to the stack.
# 'GENERATOR': means that we entered method which is actually a generator for which we'll
#              track yield pause/resume so we should add it to the stack.
# 'UNTRACKED_GENERATOR': A generator for which we'll not track pause and resume (thus
#                        it should not be added to the stack, but we can signal that
#                        it was created/finished).
LogElementType = Literal[
    "METHOD",
    "GENERATOR",
    "UNTRACKED_GENERATOR",
    "FOR",
    "FOR_STEP",
    "WHILE",
    "WHILE_STEP" "IF",
    "ELSE",
]
