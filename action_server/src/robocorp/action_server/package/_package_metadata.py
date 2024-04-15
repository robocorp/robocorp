import json
from pathlib import Path
from typing import Any, Dict


def collect_package_metadata(package_dir: Path, datadir: str) -> str | int:
    """
    Args:
        package_dir: The directory with the action package for which the
            generated metadata is required.
        datadir: The datadir to be used.

    Returns: Either the package metadata to be printed or an error code.
    """
    from fastapi.applications import FastAPI
    from robocorp.actions._protocols import ActionsListActionTypedDict

    from robocorp.action_server._actions_import import hook_on_actions_list
    from robocorp.action_server._errors_action_server import ActionServerValidationError
    from robocorp.action_server._models import Action, ActionPackage, create_db
    from robocorp.action_server.cli import _main_retcode

    args = ["start", "--db-file", ":memory:"]
    if datadir:
        args.extend(["--datadir", datadir])

    metadata: Dict[str, Any] = {}
    secrets = {}

    def on_actions_list(
        action_package: "ActionPackage",
        actions_list_result: list[ActionsListActionTypedDict],
    ):
        from robocorp.action_server._server import build_url_api_run

        action_info: ActionsListActionTypedDict
        for action_info in actions_list_result:
            managed_params_schema = action_info.get("managed_params_schema", {})
            if managed_params_schema and isinstance(managed_params_schema, dict):
                found_secrets = {}
                for k, v in managed_params_schema.items():
                    if isinstance(v, dict) and v.get("type") == "Secret":
                        found_secrets[k] = v

                if found_secrets:
                    secrets[
                        build_url_api_run(action_package.name, action_info["name"])
                    ] = {
                        "actionPackage": action_package.name,
                        "action": action_info["name"],
                        "secrets": found_secrets,
                    }

        metadata["metadata"] = {"secrets": secrets}
        metadata["metadata"]["name"] = action_package.name

    def collect_metadata_and_cancel_startup(app: FastAPI) -> bool:
        nonlocal metadata
        openapi = app.openapi()
        metadata["openapi.json"] = openapi

        return False

    before_start = [collect_metadata_and_cancel_startup]

    with create_db(":memory:") as db, hook_on_actions_list.register(on_actions_list):
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
    return json.dumps(metadata)
