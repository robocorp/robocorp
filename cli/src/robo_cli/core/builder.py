from enum import Enum
from typing import Union

from pydantic import BaseModel

from .events import (
    Assign,
    ElementArgument,
    EndElement,
    EndRun,
    EndTask,
    EndTraceback,
    Event,
    Id,
    Info,
    InitialTime,
    Log,
    LogHtml,
    StartElement,
    StartRun,
    StartTask,
    StartTime,
    StartTraceback,
    Tag,
    TracebackEntry,
    TracebackVariable,
    Version,
)


class Status(str, Enum):
    RUNNING = "RUNNING"
    PASS = "PASS"
    ERROR = "ERROR"


# TODO: Rename these to match pythonic things


class Element(BaseModel):
    name: str
    status: Status
    body: list["Element"]


class Task(BaseModel):
    name: str
    status: Status
    body: list[Element]


class Suite(BaseModel):
    name: str
    status: Status
    body: list[Task]


class Model(BaseModel):
    name: str
    status: Status
    body: list[Suite]


TreeItems = Union[Model, Suite, Task, Element]


def flatten_model(model: TreeItems, depth=0):
    nodes = [(model.name, model.status, depth)]

    depth += 1
    for child in model.body:
        nodes.extend(flatten_model(child, depth))

    return nodes


class Builder:
    def __init__(self, model: Model):
        self._model = model
        self._stack: list[TreeItems] = [model]

    def handle_event(self, event: Event):
        kind = type(event).__name__
        handler = getattr(self, f"handle_{kind}", None)
        if not handler:
            raise RuntimeError(f"Unhandled event: {kind}")
        handler(event)

    def handle_Version(self, event: Version):
        pass

    def handle_Info(self, event: Info):
        pass

    def handle_Id(self, event: Id):
        pass

    def handle_InitialTime(self, event: InitialTime):
        pass

    def handle_Log(self, event: Log):
        pass

    def handle_LogHtml(self, event: LogHtml):
        pass

    def handle_StartRun(self, event: StartRun):
        model = Suite(name=event.name, status=Status.RUNNING, body=[])

        assert isinstance(self._stack[-1], Model)
        self._stack[-1].body.append(model)
        self._stack.append(model)

    def handle_EndRun(self, event: EndRun):
        model = self._stack.pop()
        model.status = Status.ERROR if event.status == "ERROR" else Status.PASS

        # Propagate "suite" status to overall status
        # TODO: Separate end execution event or just one suite in model?
        self._stack[0].status = model.status

    def handle_StartTask(self, event: StartTask):
        model = Task(name=event.name, status=Status.RUNNING, body=[])

        assert isinstance(self._stack[-1], Suite)
        self._stack[-1].body.append(model)
        self._stack.append(model)

    def handle_EndTask(self, event: EndTask):
        model = self._stack.pop()
        model.status = Status.ERROR if event.status == "ERROR" else Status.PASS

    def handle_StartElement(self, event: StartElement):
        model = Element(name=event.name, status=Status.RUNNING, body=[])

        assert isinstance(self._stack[-1], (Task, Element))
        self._stack[-1].body.append(model)
        self._stack.append(model)

    def handle_EndElement(self, event: EndElement):
        model = self._stack.pop()
        model.status = Status.ERROR if event.status == "ERROR" else Status.PASS

    def handle_ElementArgument(self, event: ElementArgument):
        pass

    def handle_Assign(self, event: Assign):
        pass

    def handle_Tag(self, event: Tag):
        pass

    def handle_StartTime(self, event: StartTime):
        pass

    def handle_StartTraceback(self, event: StartTraceback):
        pass

    def handle_TracebackEntry(self, event: TracebackEntry):
        pass

    def handle_TracebackVariable(self, event: TracebackVariable):
        pass

    def handle_EndTraceback(self, event: EndTraceback):
        pass
