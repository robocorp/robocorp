import hashlib
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from functools import cached_property
from pathlib import Path
from typing import Any, Generic, NewType, Optional, TypeVar

from pydantic import BaseModel, Field, computed_field

LOGGER = logging.getLogger(__name__)

T = TypeVar("T")
TaskId = NewType("TaskId", str)
RunId = NewType("RunId", str)


class StatusResponse(BaseModel):
    version: str


class Serializable(ABC, Generic[T]):
    @abstractmethod
    def to_row(self) -> T:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_row(cls, fields: T):
        raise NotImplementedError


class Task(BaseModel, Serializable):
    name: str
    docs: str
    file: Path
    line: int
    input_schema: dict[str, Any] = {}
    output_schema: dict[str, Any] = {}
    enabled: bool = True

    @computed_field  # type: ignore
    @cached_property
    def task_id(self) -> TaskId:
        digest = hashlib.md5(self.name.encode("utf-8")).hexdigest()[:16]
        return TaskId(digest)

    def to_row(self):
        return [
            self.task_id,
            self.name,
            self.docs,
            str(self.file),
            self.line,
            json.dumps(self.input_schema),
            json.dumps(self.output_schema),
            self.enabled,
        ]

    @classmethod
    def from_row(cls, fields):
        task_id = fields[0]
        try:
            task = cls(
                name=fields[1],
                docs=fields[2],
                file=fields[3],
                line=fields[4],
                input_schema=json.loads(fields[5]),
                output_schema=json.loads(fields[6]),
                enabled=fields[7],
            )
        except (IndexError, ValueError):
            raise ValueError(f"Invalid task entry in database: {fields}")

        # Sanity check for generated id
        if task_id != task.task_id:
            LOGGER.warning(
                "UID mismatch in stored task: %s / %s", task_id, task.task_id
            )

        return task


class State(str, Enum):
    NOT_RUN = "NOT_RUN"
    PASS = "PASS"
    FAIL = "FAIL"


class Run(BaseModel, Serializable):
    run_id: RunId
    task_id: TaskId
    state: State
    start_time: datetime = Field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    artifacts: list[str] = []

    def to_row(self):
        return [
            self.run_id,
            self.task_id,
            self.state,
            self.start_time,
            self.end_time,
        ]

    @classmethod
    def from_row(cls, fields):
        try:
            task = cls(
                run_id=fields[0],
                task_id=fields[1],
                state=fields[2],
                start_time=fields[3],
                end_time=fields[4],
            )
        except IndexError:
            raise ValueError(f"Invalid run entry in database: {fields}")

        return task
