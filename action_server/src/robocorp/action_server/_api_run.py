import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Dict, List, Optional

import fastapi
from fastapi.params import Param
from fastapi.routing import APIRouter
from starlette.responses import FileResponse

from robocorp.action_server._models import Run

log = logging.getLogger(__name__)
run_api_router = APIRouter(prefix="/api/runs")


@run_api_router.get("", response_model=list[Run])
def list_runs():
    from ._runs_state_cache import get_global_runs_state

    global_runs_state = get_global_runs_state()
    with global_runs_state.semaphore:
        return global_runs_state.get_current_run_state()


def get_run_by_id(run_id: str) -> Run:
    try:
        from ._runs_state_cache import get_global_runs_state

        global_runs_state = get_global_runs_state()
        with global_runs_state.semaphore:
            return global_runs_state.get_run_from_id(run_id)
    except KeyError as err:
        from fastapi.exceptions import HTTPException
        from starlette import status

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


@run_api_router.get("/{run_id}/log.html")
def get_run_log_html(run_id: str = fastapi.Path(title="ID for run")):
    from fastapi.exceptions import HTTPException

    artifacts_in = _get_artifacts_dir_for_run_id(run_id)
    if artifacts_in is None:
        raise HTTPException(
            status_code=404, detail="log.html not available for requested run."
        )
    log_html = artifacts_in / "log.html"
    if not os.path.exists(log_html):
        raise HTTPException(
            status_code=404, detail="log.html not available for requested run."
        )
    return FileResponse(log_html)


def _get_artifacts_dir_for_run_id(run_id: str) -> Optional[Path]:
    from robocorp.action_server._settings import get_settings

    settings = get_settings()
    run = get_run_by_id(run_id)
    artifacts_dir = settings.artifacts_dir

    if not settings.artifacts_dir:
        log.critical(
            "Unable to get artifacts because the settings artifacts_dir is not defined."
        )
        return None

    artifacts_in = (artifacts_dir / run.relative_artifacts_dir).absolute()
    if not artifacts_in.exists():
        log.critical(
            f"Unable to get artifacts because the artifacts_dir ({artifacts_in}) "
            "does not exist."
        )
        return None

    return artifacts_in


@run_api_router.get("/{run_id}/artifacts/text-content")
def get_run_artifact_text(
    run_id: str = fastapi.Path(title="ID for run"),
    artifact_names: Optional[List[str]] = fastapi.Query(
        default=None, title="Artifact names for which the content should be gotten."
    ),
    artifact_name_regexp: Optional[str] = fastapi.Query(
        default=None,
        title="A regexp to match artifact names.",
    ),
) -> Dict[str, str]:
    artifacts_in = _get_artifacts_dir_for_run_id(run_id)
    if artifacts_in is None:
        return {}
    if artifact_names is None:
        artifact_names = []

    checked = set()

    if artifact_name_regexp:
        import re

        pattern = re.compile(artifact_name_regexp)

        # We can't use glob directly because users would be able to get contents
        # out of the artifacts dir with that.
        for artifact_info in _get_file_info_in_path(artifacts_in):
            if pattern.match(artifact_info.name):
                artifact_names.append(artifact_info.name)

    ret: Dict[str, str] = {}
    for name in artifact_names:
        if name in checked:
            continue
        checked.add(name)

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
                artifacts_in,
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
