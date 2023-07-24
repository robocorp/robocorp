import re
from pathlib import Path
from typing import Optional, Union
from urllib.parse import unquote, urlparse

import requests

PathLike = Union[str, Path]

CHUNK_SIZE = 32768


def download(
    url: str,
    path: Optional[PathLike] = None,
    overwrite: bool = False,
) -> Path:
    """Download a file from the given URL.

    If the `path` argument is not given, the file is downloaded to the
    current working directory. The filename is automatically selected
    based on either the response headers or the URL.

    Params:
        url: URL to download
        path: Path to destination file
        overwrite: Overwrite file if it already exists

    Returns:
        Path to created file
    """
    if path is not None:
        path = Path(path)
        if path.is_dir():
            dirname = path
            filename = None
        else:
            dirname = path.parent
            filename = path.name
    else:
        dirname = Path.cwd()
        filename = None

    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        # Try to resolve filename from response headers
        if filename is None:
            if content_disposition := response.headers.get("Content-Disposition"):
                if match := re.search(r"filename=\"(.+)\"", content_disposition):
                    filename = match.group(1)

        # Try to parse filename from download URL
        if filename is None:
            parts = urlparse(url).path.split("/")
            for part in reversed(parts):
                part = unquote(part)
                if part.strip():
                    filename = part
                    break

        # Fallback value (unlikely)
        if filename is None:
            filename = "unknown"

        output = dirname / filename
        if output.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {output}")

        dirname.mkdir(parents=True, exist_ok=True)
        with open(output, "wb") as fd:
            for chunk in response.iter_content(CHUNK_SIZE):
                if chunk:  # Filter out keep-alive new chunks
                    fd.write(chunk)

        return output
