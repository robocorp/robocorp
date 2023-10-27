import json
from typing import Optional

from ._database import list_tasks, update_tasks
from ._models import Task, TaskId
from ._process import Process
from ._settings import get_settings


class Tasks:
    _instance: Optional["Tasks"] = None

    @classmethod
    def get_instance(cls) -> "Tasks":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self) -> None:
        self._tasks: dict[TaskId, Task] = {}

    @property
    def tasks(self) -> dict[TaskId, Task]:
        return dict(self._tasks)

    def collect(self):
        # TODO: While this could technically be run through the Python API,
        #  it doesn't currently expose it publicly, and we also want to
        #  ensure the lifecycle methods are called correctly
        settings = get_settings()
        proc = Process(args=["python", "-m", "robocorp.tasks", "list", str(settings.tasks)])
        stdout, _ = proc.run()

        tasks = [Task(**fields) for fields in json.loads(stdout)]
        update_tasks(tasks)

        self._tasks = {task.task_id: task for task in list_tasks()}
