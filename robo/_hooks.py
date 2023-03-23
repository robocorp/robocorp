from robo._callback import Callback
from robo._protocols import (
    IOnTaskFuncFoundCallback,
    IBeforeCollectTasksCallback,
    IBeforeTaskRunCallback,
    IAfterTaskRunCallback,
)


# Called as on_task_func_found(task: ITask)
on_task_func_found: IOnTaskFuncFoundCallback = Callback()

# Called as before_collect_tasks(path: Path, task_name: str)
before_collect_tasks: IBeforeCollectTasksCallback = Callback()

# Called as before_collect_tasks(task: ITask)
before_task_run: IBeforeTaskRunCallback = Callback()

# Called as after_task_run(task: ITask)
after_task_run: IAfterTaskRunCallback = Callback()
