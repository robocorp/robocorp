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
    START_RUN = "SR"
    END_RUN = "ER"
    START_TASK = "ST"
    END_TASK = "ET"
    START_ELEMENT = "SE"
    END_ELEMENT = "EE"
    ELEMENT_ARGUMENT = "EA"
    ASSIGN = "AS"
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


class StartRun(BaseModel):
    name: str
    time_delta_in_seconds: float


class EndRun(BaseModel):
    status: str
    time_delta_in_seconds: float


class StartTask(BaseModel):
    name: str
    libname: str
    source: str
    lineno: int
    time_delta_in_seconds: float


class EndTask(BaseModel):
    status: str
    message: str
    time_delta_in_seconds: float


class StartElement(BaseModel):
    name: str
    libname: str
    type: str
    doc: str
    source: str
    lineno: int
    time_delta_in_seconds: float


class EndElement(BaseModel):
    status: str
    time_delta_in_seconds: float


class ElementArgument(BaseModel):
    name: str
    value: str


class Assign(BaseModel):
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
    StartRun,
    EndRun,
    StartTask,
    EndTask,
    StartElement,
    EndElement,
    ElementArgument,
    Assign,
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
    MessageType.START_RUN: StartRun,
    MessageType.END_RUN: EndRun,
    MessageType.START_TASK: StartTask,
    MessageType.END_TASK: EndTask,
    MessageType.START_ELEMENT: StartElement,
    MessageType.END_ELEMENT: EndElement,
    MessageType.ELEMENT_ARGUMENT: ElementArgument,
    MessageType.ASSIGN: Assign,
    MessageType.TAG: Tag,
    MessageType.START_TIME: StartTime,
    MessageType.START_TRACEBACK: StartTraceback,
    MessageType.TRACEBACK_ENTRY: TracebackEntry,
    MessageType.TRACEBACK_VARIABLE: TracebackVariable,
    MessageType.END_TRACEBACK: EndTraceback,
}
