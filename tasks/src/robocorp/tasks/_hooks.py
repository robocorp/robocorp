from ._callback import Callback
from ._protocols import (
    IOnTaskFuncFoundCallback,
    IBeforeCollectTasksCallback,
    IBeforeTaskRunCallback,
    IAfterTaskRunCallback,
    IBeforeAllTasksRunCallback,
    IAfterAllTasksRunCallback,
)


# Called as on_task_func_found(task: ITask)
on_task_func_found: IOnTaskFuncFoundCallback = Callback()

# Called as before_collect_tasks(path: Path, task_names: Set[str])
before_collect_tasks: IBeforeCollectTasksCallback = Callback()

# Called as before_all_tasks_run(tasks: List[ITask])
before_all_tasks_run: IBeforeAllTasksRunCallback = Callback()

# Called as before_collect_tasks(task: ITask)
before_task_run: IBeforeTaskRunCallback = Callback()

# Called as after_task_run(task: ITask)
# Note that this one is done in reversed registry order (as is usually
# expected from tear-downs).
after_task_run: IAfterTaskRunCallback = Callback(reversed=True)

# Called as after_all_tasks_run(tasks: List[ITask])
# Note that this one is done in reversed registry order (as is usually
# expected from tear-downs).
after_all_tasks_run: IAfterAllTasksRunCallback = Callback(reversed=True)
