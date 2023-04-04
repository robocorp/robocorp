import json
import logging
from typing import Callable, TypedDict

from .output import KIND_TO_EVENT, Event
from .process import Process

LOGGER = logging.getLogger(__name__)


class Task(TypedDict):
    name: str
    line: int
    file: str
    docs: str


def list_tasks(env: dict[str, str]) -> list[Task]:
    proc = Process(
        ["python", "-m", "robo", "list", "tasks.py"],
        env=env,
    )
    stdout, _ = proc.run()
    tasks = json.loads(stdout)
    return tasks


def run_task(env: dict[str, str], taskname: str, on_event: Callable[[Event], None]):
    proc = Process(
        ["python", "-m", "robo", "run", "tasks.py", "-t", taskname],
        env=env,
    )

    def handle_line(line: str):
        try:
            payload = json.loads(line)
            klass = KIND_TO_EVENT[payload["message_type"]]
            event = klass.parse_obj(payload)
            on_event(event)
        except Exception as exc:
            LOGGER.debug(f"Unhandled exception in listener: {exc}")

    proc.on_stdout(handle_line)
    proc.run()
