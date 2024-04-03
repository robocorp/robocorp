import json
from pathlib import Path


def collect_package_metadata(package_dir: Path, datadir: str) -> str | int:
    """
    Args:
        package_dir: The directory with the action package for which the
            generated metadata is required.
        datadir: The datadir to be used.

    Returns: Either the package metadata to be printed or an error code.
    """
    from fastapi.applications import FastAPI

    from robocorp.action_server._errors_action_server import ActionServerValidationError
    from robocorp.action_server._models import Action, create_db
    from robocorp.action_server.cli import _main_retcode

    args = ["start", "--db-file", ":memory:"]
    if datadir:
        args.extend(["--datadir", datadir])

    metadata: str = ""

    def collect_metadata_and_cancel_startup(app: FastAPI) -> bool:
        nonlocal metadata
        openapi = app.openapi()
        metadata = json.dumps({"openapi.json": openapi})

        return False

    before_start = [collect_metadata_and_cancel_startup]

    with create_db(":memory:") as db:
        returncode = _main_retcode(
            args, is_subcommand=True, use_db=db, before_start=before_start
        )
        if returncode != 0:
            return returncode
        if not db.all(Action):
            raise ActionServerValidationError("No actions found.")

    if not metadata:
        raise ActionServerValidationError(
            "It was not possible to collect the metadata."
        )
    return metadata
