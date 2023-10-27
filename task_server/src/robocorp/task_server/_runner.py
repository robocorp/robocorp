import logging
import uuid
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Optional

from . import _database as db
from ._models import Run, RunId, State, Task
from ._process import Process
from ._settings import get_settings

LOGGER = logging.getLogger(__name__)


class Runner:
    _instance: Optional["Runner"] = None

    @classmethod
    def get_instance(cls) -> "Runner":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self) -> None:
        settings = get_settings()
        self._artifacts = settings.metadata / "artifacts"
        self._runs: dict[RunId, Run] = {}
        self._procs: dict[RunId, Process] = {}

    @property
    def artifacts(self) -> Path:
        return self._artifacts
 
    @property
    def runs(self) -> dict[RunId, Run]:
        return dict(self._runs)

    def load_history(self):
        self._runs = {}
        for run in db.list_runs():
            self._parse_artifacts(run)
            self._runs[run.run_id] = run

    def run(self, task: Task, payload: Any) -> Run:
        settings = get_settings()
        self._artifacts.mkdir(parents=True, exist_ok=True)

        run_id = RunId(str(uuid.uuid4()))
        run = Run(
            run_id=run_id,
            task_id=task.task_id,
            state=State.NOT_RUN,
        )

        args = self._to_cli_args(payload)
        proc = Process(
            args=[
                "python",
                "-m",
                "robocorp.tasks",
                "run",
                "--console-colors",
                "plain",
                "--task",
                task.name,
                "--output-dir",
                str(self._artifacts / run_id),
                str(settings.tasks),
                "--",
                *args,
            ]
        )

        proc.add_listener(partial(logging.info, f"run[{run_id}]: %s"))

        db.start_run(run)
        self._runs[run_id] = run
        self._procs[run_id] = proc

        try:
            proc.run()
            run.state = State.PASS
        except Exception:
            run.state = State.FAIL
        finally:
            run.end_time = datetime.now()
            self._parse_artifacts(run)
            db.end_run(run)

        return run

    def _parse_artifacts(self, run: Run):
        artifacts: list[str] = []
        dirname = self.artifacts / run.run_id
        if dirname.exists():
            for path in dirname.glob("*"):
                if path.is_file():
                    artifacts.append(path.name)
        run.artifacts = artifacts

    @staticmethod
    def _to_cli_args(payload: Any) -> list[str]:
        args = []
        if isinstance(payload, dict):
            for key, val in payload.items():
                args.extend([f"--{key}", f"{val}"])
        elif isinstance(payload, list):
            args = [str(val) for val in payload]
        elif payload is None:
            pass
        else:
            args.append(str(payload))

        return args
