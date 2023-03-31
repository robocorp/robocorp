from pathlib import Path
import requests
from typing import Any, Optional, Union


def download(
    url: str,
    target_file: Optional[str] = None,
    stream=True,
) -> dict:
    filename = Path(target_file) if target_file else Path(url.split('/')[-1])
    filename = str(filename)
    # NOTE the stream=True parameter below
    with requests.get(url, stream=stream) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk:
                f.write(chunk)
    return filename


