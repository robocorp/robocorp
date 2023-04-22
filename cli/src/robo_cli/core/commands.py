import json
from typing import Callable, TypedDict

from robo_cli.process import Process

from .events import TYPE_TO_EVENT, Event


class Task(TypedDict):
    name: str
    line: int
    file: str
    docs: str


def list_tasks(env: dict[str, str]) -> list[Task]:
    proc = Process(
        ["python", "-m", "robocorp.tasks", "list", "tasks.py"],
        env=env,
    )
    stdout, _ = proc.run()
    tasks = json.loads(stdout)
    return tasks


def run_task(env: dict[str, str], taskname: str, on_event: Callable[[Event], None]):
    proc = Process(
        ["python", "-m", "robocorp.tasks", "run", "tasks.py", "-t", taskname],
        env=env,
    )

    def handle_line(line: str):
        payload = json.loads(line)
        klass = TYPE_TO_EVENT[payload["message_type"]]
        event = klass.parse_obj(payload)
        on_event(event)

    proc.on_stdout(handle_line)
    proc.run()
