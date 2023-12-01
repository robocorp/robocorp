from typing import Annotated, List

import fastapi
from fastapi.params import Query
from fastapi.routing import APIRouter
from starlette import status

from robocorp.action_server._models import Run

run_api_router = APIRouter(prefix="/api/runs")


@run_api_router.get("/", response_model=List[Run])
def list_runs(
    page: Annotated[int, Query(description="The page to be gotten")] = 1,
    limit: Annotated[
        int, Query(description="The limit of runs to be gotten", le=200)
    ] = 50,
):
    from robocorp.action_server._models import get_db

    offset = (page - 1) * limit
    db = get_db()
    with db.connect():
        # We're running in the threadpool used by fast api, so, we need
        # to make a new connection (maybe it'd make sense to create a
        # connection pool instead of always creating a new connection...).
        return db.all(Run, offset=offset, limit=limit)


def get_run_by_id(run_id: str) -> Run:
    from fastapi.exceptions import HTTPException

    from robocorp.action_server._models import get_db

    try:
        db = get_db()
        with db.connect():
            return db.first(
                Run,
                "SELECT * FROM run WHERE id = ?",
                [run_id],
            )
    except KeyError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown run id: {run_id}",
        ) from err


@run_api_router.get("/{run_id}", response_model=Run)
def show_run(run_id: str = fastapi.Path(title="ID for run")):
    # Note that we want to use
    return get_run_by_id(run_id)
