from pathlib import Path
import requests


def download_file(url: str, target_dir: Path, target_filename: str) -> str:
    """
    Downloads a file from the given url into the given folder with given filename.
    """
    target_dir.mkdir(exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()  # This will raise an exception if the request fails
    local_filename = Path(target_dir, target_filename)
    with open(local_filename, "wb") as f:
        f.write(response.content)  # Write the content of the response to a file
    return local_filename
