from contextlib import contextmanager
from typing import Optional

from robocorp import log

from ._protocols import ITask


def _log_before_task_run(task: ITask):
    log.start_task(
        task.name,
        task.module_name,
        task.filename,
        task.method.__code__.co_firstlineno + 1,
        getattr(task.method, "__doc__", ""),
    )


def _log_after_task_run(task: ITask):
    status = task.status
    log.end_task(task.name, task.module_name, status, task.message)


@contextmanager
def setup_cli_auto_logging(config: Optional[log.AutoLogConfigBase]):
    # This needs to be called before importing code which needs to show in the log
    # (user or library).

    from robocorp.tasks._hooks import after_task_run, before_task_run

    with log.setup_auto_logging(config):
        with before_task_run.register(_log_before_task_run), after_task_run.register(
            _log_after_task_run
        ):
            try:
                yield
            finally:
                log.close_log_outputs()
