from pathlib import Path
from urllib.parse import urlparse
from typing import Any, Optional, Union


def _create_or_overwrite_target_file(
    self,
    path: str,
    response: Any,
    overwrite: bool,
) -> None:
    CHUNK_SIZE = 32768
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    file_exists = Path(path).is_file()
    if not file_exists or (file_exists and overwrite):
        with open(path, "wb") as f:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)


def download(
    self,
    url: str,
    target_file: Optional[str] = None,
    verify: Union[bool, str] = True,
    force_new_session: bool = False,
    overwrite: bool = False,
    stream: bool = False,
    **kwargs,
) -> dict:
    response = self.http_get(
        url,
        verify=verify,
        force_new_session=force_new_session,
        overwrite=overwrite,
        stream=stream,
        **kwargs,
    )

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

    self._create_or_overwrite_target_file(dirname / filename, response, overwrite)

    return response
