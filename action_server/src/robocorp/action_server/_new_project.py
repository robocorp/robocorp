import io
import logging
import os
import sys
import zipfile
from urllib.request import urlopen

TEMPLATE_URL = (
    "https://github.com/robocorp/template-action/archive/refs/heads/master.zip"
)

log = logging.getLogger(__name__)


def create_new_project(directory: str = "."):
    try:
        if not directory:
            directory = input("Name of the project: ")
            if not directory:
                raise RuntimeError("The name of the project was not given.")

        if directory != ".":
            if os.path.exists(directory) and os.listdir(directory):
                raise RuntimeError(
                    f"The folder: {directory} already exists and is not empty."
                )

        download_and_unzip(TEMPLATE_URL, directory)

        log.info("✅ Project created")
    except KeyboardInterrupt:
        log.debug("Operation cancelled")
    except Exception as e:
        log.critical(f"Error creating the project: {e}")


def download_and_unzip(url: str, directory: str = "."):
    """
    Downloads a zip file from the given URL to memory,
    extracts files one by one and makes .sh files executable.
    """

    created_parents = set()
    with urlopen(url) as response:
        with io.BytesIO(response.read()) as zip_buffer:
            with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
                namelist = list(zip_ref.namelist())

                for path_in_zip in namelist:
                    parts = path_in_zip.split("/", 1)
                    if len(parts) < 2 or not parts[1]:
                        continue

                    # i.e.: Remove the root dir from the .zip
                    # (which is something as template-action-master)
                    write_to = os.path.join(directory, parts[1])

                    if path_in_zip.endswith("/"):
                        created_parents.add(write_to)
                        os.makedirs(write_to, exist_ok=True)
                        continue
                    else:
                        parent_dir = os.path.dirname(write_to)
                        if parent_dir and parent_dir not in created_parents:
                            created_parents.add(parent_dir)
                            os.makedirs(parent_dir, exist_ok=True)

                    with zip_ref.open(path_in_zip, "r") as zip_file:
                        data = zip_file.read()

                    with open(write_to, "wb") as out_file:
                        out_file.write(data)

                    # Make .sh files executable
                    if path_in_zip.endswith(".sh"):
                        if sys.platform != "win32":
                            os.chmod(write_to, 0o755)


# if __name__ == "__main__":
#     download_and_unzip(TEMPLATE_URL, "ra")
