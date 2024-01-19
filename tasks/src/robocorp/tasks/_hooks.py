import os
from logging import getLogger

from ._callback import Callback
from ._protocols import (
    IAfterAllTasksRunCallback,
    IAfterTaskRunCallback,
    IBeforeAllTasksRunCallback,
    IBeforeCollectTasksCallback,
    IBeforeTaskRunCallback,
    IOnTaskFuncFoundCallback,
)

logger = getLogger(__name__)


class SessionCallback(Callback):
    def __init__(self, skip_env_name, skip_always, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._called_already = set()
        self._skip_env_name = skip_env_name
        self._skip_always = skip_always

    def unregister(self, callback):
        self._called_already.discard(callback)
        super().unregister(callback)

    def __call__(self, *args, **kwargs):
        if self._reversed:
            iter_in = reversed(self._callbacks)
        else:
            iter_in = self._callbacks

        skip = os.environ.get(self._skip_env_name, "") in ("true", "1")

        if skip and self._skip_always:
            return

        for c in iter_in:
            if skip and c in self._called_already:
                continue
            self._called_already.add(c)

            try:
                c(*args, **kwargs)
            except Exception:
                logger.exception(f"Error calling: {c}.")
                if self.raise_exceptions:
                    raise


# Called as on_task_func_found(task: ITask)
on_task_func_found: IOnTaskFuncFoundCallback = Callback(raise_exceptions=True)

# Called as before_collect_tasks(path: Path, task_names: Set[str])
before_collect_tasks: IBeforeCollectTasksCallback = Callback()

# Called as before_all_tasks_run(tasks: List[ITask])
before_all_tasks_run: IBeforeAllTasksRunCallback = SessionCallback(
    "RC_TASKS_SKIP_SESSION_SETUP", False, raise_exceptions=True
)

# Called as before_task_run(task: ITask)
before_task_run: IBeforeTaskRunCallback = Callback(raise_exceptions=True)

# Called as after_task_run(task: ITask)
# Note that this one is done in reversed registry order (as is usually
# expected from tear-downs).
after_task_run: IAfterTaskRunCallback = Callback(reversed=True)

# Called as after_all_tasks_run(tasks: List[ITask])
# Note that this one is done in reversed registry order (as is usually
# expected from tear-downs).
after_all_tasks_run: IAfterAllTasksRunCallback = SessionCallback(
    "RC_TASKS_SKIP_SESSION_TEARDOWN", True, reversed=True
)
