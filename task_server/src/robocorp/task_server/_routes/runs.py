from typing import Any

import jsonschema
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from .._dependencies import get_run_by_id, get_task_by_id
from .._errors import RequestError, ErrorCode
from .._models import Run, TaskId
from .._runner import Runner

router = APIRouter(prefix="/runs")


class StartRunRequest(BaseModel):
    task_id: TaskId
    payload: Any

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task_id": "",
                    "payload": {},
                }
            ]
        }
    }


@router.get("/", response_model=list[Run])
def list_runs():
    runner = Runner.get_instance()
    return list(runner.runs.values())


@router.post("/start", response_model=Run)
def start_run(request: StartRunRequest):
    task = get_task_by_id(request.task_id)
    if not task.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task not enabled [name={task.name},id={task.task_id}]",
        )

    try:
        jsonschema.validate(request.payload, task.input_schema)
    except Exception as exc:
        raise RequestError(ErrorCode.VALIDATION_ERROR, str(exc))

    runner = Runner.get_instance()
    return runner.run(task, request.payload)


@router.get("/{run_id}", response_model=Run)
def show_run(run: Run = Depends(get_run_by_id)):
    return run
