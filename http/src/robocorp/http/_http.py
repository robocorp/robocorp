from pathlib import Path
import requests
from urllib.parse import urlparse

from typing import Any, Optional
from robocorp.http._types import PathType


def _create_or_overwrite_target_file(
    path: PathType,
    response: Any,
    overwrite: bool,
) -> Path:
    CHUNK_SIZE = 32768
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.is_file()
    if not file_exists or (file_exists and overwrite):
        with open(path, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
    return path


def download(
    url: str,
    target_file: Optional[PathType] = None,
    overwrite: bool = False,
    stream=True,
) -> Path:
    dirname = Path()
    filename = None

    if target_file is not None:
        target = Path(target_file)
        if target.is_dir():
            dirname = target
        else:
            dirname = target.parent
            filename = target.name

    if filename is None:
        filename = urlparse(url).path.rsplit("/", 1)[-1] or "downloaded.html"

    with requests.get(url, stream=stream) as response:
        response.raise_for_status()
        path = _create_or_overwrite_target_file(dirname / filename, response, overwrite)

    return path
