import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Dict, List, Optional

import fastapi
from fastapi.params import Param, Query
from fastapi.routing import APIRouter
from starlette import status
from starlette.responses import FileResponse

from robocorp.action_server._models import Run

log = logging.getLogger(__name__)
run_api_router = APIRouter(prefix="/api/runs")


@run_api_router.get("", response_model=List[Run])
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


@dataclass
class ArtifactInfo:
    name: str
    size_in_bytes: int


def _scandir_recursive(path):
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from _scandir_recursive(entry.path)
        else:
            yield entry


def _get_file_info_in_path(path: Path) -> List[ArtifactInfo]:
    file_names = []
    for entry in _scandir_recursive(path):
        try:
            if entry.is_file():
                size = entry.stat().st_size
                name = Path(entry.path).relative_to(path).as_posix()
                file_names.append(ArtifactInfo(name, size))
        except Exception:
            log.exception(f"Unable to get information from: {entry}.")
            continue
    return file_names


@run_api_router.get("/{run_id}/artifacts")
def get_run_artifacts(
    run_id: str = fastapi.Path(title="ID for run"),
) -> Annotated[
    List[ArtifactInfo],
    Param(
        description="""Provides a list with the artifacts available
for a given run (i.e.: [{'name': '__action_server_output.txt', 'size_in_bytes': 22}])
"""
    ),
]:
    from robocorp.action_server._settings import get_settings

    settings = get_settings()
    run = get_run_by_id(run_id)
    artifacts_dir = settings.artifacts_dir

    if not settings.artifacts_dir:
        log.critical(
            "Unable to get artifacts because the settings artifacts_dir is not defined."
        )
        return []

    artifacts_in = artifacts_dir / run.relative_artifacts_dir
    if not artifacts_in.exists():
        log.critical(
            f"Unable to get artifacts because the artifacts_dir ({artifacts_in}) "
            "does not exist."
        )
        return []

    return _get_file_info_in_path(artifacts_in)


@run_api_router.get("/{run_id}/artifacts/text-content")
def get_run_artifact_text(
    run_id: str = fastapi.Path(title="ID for run"),
    artifact_names: List[str] = fastapi.Query(
        title="Artifact names for which the content should be gotten."
    ),
) -> Dict[str, str]:
    from robocorp.action_server._settings import get_settings

    settings = get_settings()
    run = get_run_by_id(run_id)
    artifacts_dir = settings.artifacts_dir

    if not settings.artifacts_dir:
        log.critical(
            "Unable to get artifacts because the settings artifacts_dir is not defined."
        )
        return {}

    artifacts_in = (artifacts_dir / run.relative_artifacts_dir).absolute()
    if not artifacts_in.exists():
        log.critical(
            f"Unable to get artifacts because the artifacts_dir ({artifacts_in}) "
            "does not exist."
        )
        return {}

    ret: Dict[str, str] = {}
    for name in artifact_names:
        f = (artifacts_in / name).absolute()
        if not f.exists():
            log.critical(f"Unable to get artifact because it does not exist: {f}")
            continue

        try:
            Path(f).relative_to(artifacts_in)
        except ValueError:
            log.critical(
                "Unable to get artifact (%s) because it does not point to a folder "
                "inside of the artifacts dir (%s).",
                f,
                artifacts_dir,
            )
            continue

        try:
            ret[name] = f.read_text("utf-8", "replace")
        except Exception:
            log.critical("Unable to read artifact: %s as text.", f)

            continue

    return ret


@run_api_router.get("/{run_id}/artifacts/binary-content", response_class=FileResponse)
def get_run_artifact_binary(
    run_id: str = fastapi.Path(title="ID for run"),
    artifact_name: str = fastapi.Query(
        title="Artifact name for which the content should be gotten."
    ),
):
    from robocorp.action_server._settings import get_settings

    settings = get_settings()
    run = get_run_by_id(run_id)
    artifacts_dir = settings.artifacts_dir

    if not settings.artifacts_dir:
        log.critical(
            "Unable to get artifacts because the settings artifacts_dir is not defined."
        )
        return None

    artifacts_in = artifacts_dir / run.relative_artifacts_dir
    if not artifacts_in.exists():
        log.critical(
            f"Unable to get artifacts because the artifacts_dir ({artifacts_in}) "
            "does not exist."
        )
        return None

    f = (artifacts_in / artifact_name).absolute()
    if not f.exists():
        log.critical(f"Unable to get artifact because it does not exist: {f}")
        return None

    try:
        Path(f).relative_to(artifacts_in)
    except ValueError:
        log.critical(
            "Unable to get artifact (%s) because it does not point to a folder "
            "inside of the artifacts dir (%s).",
            f,
            artifacts_dir,
        )
        return None

    return FileResponse(f)
