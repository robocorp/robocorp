from contextlib import contextmanager
from robo._protocols import ITask


def _log_before_task_run(task: ITask):
    import robocorp_logging

    robocorp_logging.log_start_suite(
        task.package_name, task.package_name, task.filename
    )
    robocorp_logging.log_start_task(
        task.name,
        f"{task.package_name}.{task.name}",
        task.method.__code__.co_firstlineno,
        [],
    )


def _log_after_task_run(task: ITask):
    import robocorp_logging

    status = task.status
    robocorp_logging.log_end_task(
        task.name, f"{task.package_name}.{task.name}", status, task.message
    )
    robocorp_logging.log_end_suite(task.package_name, task.package_name, status)


@contextmanager
def setup_auto_logging():
    import robocorp_logging
    from robo._hooks import before_task_run
    from robo._hooks import after_task_run

    # This needs to be called before importing code which needs to show in the log
    # (user or library).
    from robocorp_logging import Filter

    with robocorp_logging.setup_auto_logging(
        # TODO: Some bug is preventing this from working.
        # filters=[Filter(name="RPA", exclude=False, is_path=False)]
    ):
        with before_task_run.register(_log_before_task_run), after_task_run.register(
            _log_after_task_run
        ):
            try:
                yield
            finally:
                robocorp_logging.close_log_outputs()
