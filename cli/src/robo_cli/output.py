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
    START_KEYWORD = "SK"
    END_KEYWORD = "EK"
    KEYWORD_ARGUMENT = "KA"
    ASSIGN_KEYWORD = "AS"
    TAG = "TG"
    START_TIME = "S"


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


class StartKeyword(BaseModel):
    name: str
    libname: str
    keyword_type: str
    doc: str
    source: str
    lineno: int
    time_delta_in_seconds: float


class EndKeyword(BaseModel):
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
    StartKeyword,
    EndKeyword,
    KeywordArgument,
    AssignKeyword,
    Tag,
    StartTime,
]

KIND_TO_EVENT: dict[MessageType, Type[Event]] = {
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
    MessageType.START_KEYWORD: StartKeyword,
    MessageType.END_KEYWORD: EndKeyword,
    MessageType.KEYWORD_ARGUMENT: KeywordArgument,
    MessageType.ASSIGN_KEYWORD: AssignKeyword,
    MessageType.TAG: Tag,
    MessageType.START_TIME: StartTime,
}
