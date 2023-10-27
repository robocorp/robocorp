from fastapi import HTTPException, Path, status

from ._models import Run, RunId, Task, TaskId
from ._runner import Runner
from ._tasks import Tasks


def get_task_by_id(task_id: TaskId = Path(title="ID for task")) -> Task:
    try:
        tasks = Tasks.get_instance()
        return tasks.tasks[task_id]
    except KeyError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown task id: {task_id}",
        ) from err


def get_run_by_id(run_id: RunId = Path(title="ID for task run")) -> Run:
    try:
        runner = Runner.get_instance()
        return runner.runs[run_id]
    except KeyError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown run id: {run_id}",
        ) from err
