from robo._callback import Callback
from robo._protocols import IOnTaskFuncFoundCallback, IBeforeCollectTasksCallback


# Called as on_task_func_found(task: ITask)
on_task_func_found: IOnTaskFuncFoundCallback = Callback()


# Called as before_collect_tasks(path: Path, task_name: str)
before_collect_tasks: IBeforeCollectTasksCallback = Callback()
