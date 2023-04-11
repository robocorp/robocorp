from contextlib import contextmanager
from robo._protocols import ITask


def _log_before_task_run(task: ITask):
    import robo_log

    robo_log.start_suite(
        task.module_name, task.module_name, task.filename
    )
    robo_log.start_task(
        task.name,
        f"{task.module_name}.{task.name}",
        task.method.__code__.co_firstlineno,
        [],
    )


def _log_after_task_run(task: ITask):
    import robo_log

    status = task.status
    robo_log.end_task(
        task.name, f"{task.module_name}.{task.name}", status, task.message
    )
    robo_log.end_suite(task.module_name, task.module_name, status)


@contextmanager
def setup_auto_logging():
    import robo_log
    from robo._hooks import before_task_run
    from robo._hooks import after_task_run

    # This needs to be called before importing code which needs to show in the log
    # (user or library).
    from robo_log import Filter

    with robo_log.setup_auto_logging(
        # TODO: Some bug is preventing this from working.
        # filters=[Filter(name="RPA", exclude=False, is_path=False)]
    ):
        with before_task_run.register(_log_before_task_run), after_task_run.register(
            _log_after_task_run
        ):
            try:
                yield
            finally:
                robo_log.close_log_outputs()
