from enum import Enum
from typing import Type, Union

from pydantic import BaseModel


class MessageType(str, Enum):
    VERSION = "V"
    INFO = "I"
    ID = "ID"
    INITIAL_TIME = "T"
    LOG = "L"
    LOG_HTML = "LH"
    START_SUITE = "SS"
    END_SUITE = "ES"
    START_TASK = "ST"
    END_TASK = "ET"
    START_ELEMENT = "SE"
    END_ELEMENT = "EE"
    KEYWORD_ARGUMENT = "KA"
    ASSIGN_KEYWORD = "AS"
    TAG = "TG"
    START_TIME = "S"
    START_TRACEBACK = "STB"
    TRACEBACK_ENTRY = "TBE"
    TRACEBACK_VARIABLE = "TBV"
    END_TRACEBACK = "ETB"


class Version(BaseModel):
    version: str


class Info(BaseModel):
    info: str


class Id(BaseModel):
    part: int
    id: str


class InitialTime(BaseModel):
    initial_time: str


class Log(BaseModel):
    level: str
    message: str
    time_delta_in_seconds: float


class LogHtml(BaseModel):
    level: str
    message: str
    time_delta_in_seconds: float


class StartSuite(BaseModel):
    name: str
    suite_id: str
    suite_source: str
    time_delta_in_seconds: float


class EndSuite(BaseModel):
    status: str
    time_delta_in_seconds: float


class StartTask(BaseModel):
    name: str
    suite_id: str
    lineno: int
    time_delta_in_seconds: float


class EndTask(BaseModel):
    status: str
    message: str
    time_delta_in_seconds: float


class StartElement(BaseModel):
    name: str
    libname: str
    keyword_type: str
    doc: str
    source: str
    lineno: int
    time_delta_in_seconds: float


class EndElement(BaseModel):
    status: str
    time_delta_in_seconds: float


class KeywordArgument(BaseModel):
    argument: str


class AssignKeyword(BaseModel):
    assign: str


class Tag(BaseModel):
    tag: str


class StartTime(BaseModel):
    start_time_delta: float


class StartTraceback(BaseModel):
    message: str


class TracebackEntry(BaseModel):
    source: str
    lineno: int
    method: str
    line_content: str


class TracebackVariable(BaseModel):
    variable_name: str
    variable_value: str


class EndTraceback(BaseModel):
    pass  # No public fields


Event = Union[
    Version,
    Info,
    Id,
    InitialTime,
    Log,
    LogHtml,
    StartSuite,
    EndSuite,
    StartTask,
    EndTask,
    StartElement,
    EndElement,
    KeywordArgument,
    AssignKeyword,
    Tag,
    StartTime,
    StartTraceback,
    TracebackEntry,
    TracebackVariable,
    EndTraceback,
]

TYPE_TO_EVENT: dict[MessageType, Type[Event]] = {
    MessageType.VERSION: Version,
    MessageType.INFO: Info,
    MessageType.ID: Id,
    MessageType.INITIAL_TIME: InitialTime,
    MessageType.LOG: Log,
    MessageType.LOG_HTML: LogHtml,
    MessageType.START_SUITE: StartSuite,
    MessageType.END_SUITE: EndSuite,
    MessageType.START_TASK: StartTask,
    MessageType.END_TASK: EndTask,
    MessageType.START_ELEMENT: StartElement,
    MessageType.END_ELEMENT: EndElement,
    MessageType.KEYWORD_ARGUMENT: KeywordArgument,
    MessageType.ASSIGN_KEYWORD: AssignKeyword,
    MessageType.TAG: Tag,
    MessageType.START_TIME: StartTime,
    MessageType.START_TRACEBACK: StartTraceback,
    MessageType.TRACEBACK_ENTRY: TracebackEntry,
    MessageType.TRACEBACK_VARIABLE: TracebackVariable,
    MessageType.END_TRACEBACK: EndTraceback,
}
