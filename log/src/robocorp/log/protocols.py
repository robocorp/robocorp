from types import TracebackType
from typing import Literal, Protocol, Sequence, Union

ExcInfo = tuple[type[BaseException], BaseException, TracebackType]
OptExcInfo = Union[ExcInfo, tuple[None, None, None]]

LogHTMLStyle = Literal["standalone", "vscode"]


class IReadLines(Protocol):
    def readlines(self) -> Sequence[str]:
        pass


class IContextErrorReport(Protocol):
    def show_error(self, message: str):
        pass


# Note: this is a bit messy as we're mixing task states with log levels.
# Note2: This is for the log.html and not really for user APIs.
class Status:
    NOT_RUN = "NOT_RUN"  # Initial status for a task which is not run.
    PASS = "PASS"  # Used for task pass
    FAIL = "FAIL"  # Used for task failure

    ERROR = "ERROR"  # log.critical
    INFO = "INFO"  # log.info
    WARN = "WARN"  # log.warn
    DEBUG = "DEBUG"  # log.debug


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
    "WHILE_STEP",
    "IF",
    "ELSE",
    "ASSERT_FAILED",
]
