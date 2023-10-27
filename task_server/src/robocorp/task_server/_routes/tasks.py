from fastapi import APIRouter, Depends

from .._dependencies import get_task_by_id
from .._models import Task, TaskId
from .._tasks import Tasks

router = APIRouter(prefix="/tasks")


@router.get("/", response_model=dict[TaskId, Task])
def list_tasks():
    return Tasks.get_instance().tasks


@router.get("/{task_id}", response_model=Task)
def show_task(task: Task = Depends(get_task_by_id)):
    return task
