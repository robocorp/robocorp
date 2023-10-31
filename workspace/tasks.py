from pathlib import Path

from invoke import task

from devutils.invoke_utils import build_common_tasks


globals().update(
    build_common_tasks(Path(__file__).absolute().parent, "robocorp.storage")
)

OPENAPI_JSON = "https://robocorp.com/api/openapi.json"
TYPES_MAPPING = {
    "Next": "StrictStr",
    "HasMore": "StrictBool",
}


@task
def generate_api_client(ctx, minimal_update: bool = True, dry_run: bool = False):
    """Generate a Python OpenAPI client over the new Robocorp API."""
    types_mapping = ",".join(
        [f"{key}=pydantic.{value}" for key, value in TYPES_MAPPING.items()]
    )
    opts_list = [
        "-g python",
        f"-i {OPENAPI_JSON}",
        "-c openapiconf.yaml",
        "--skip-validate-spec",
        "-o src",
        "-t templates",
        f"--type-mappings {types_mapping}",
    ]
    if minimal_update:
        opts_list.append("--minimal-update")
    if dry_run:
        opts_list.append("--dry-run")
    opts = " ".join(opts_list)
    # FIXME(cmin764, 31 Oct 2023): Get back to PIP provided `openapi-generator` script
    #  once we fork the project to update to the latest CLI JAR wrapped binary version.
    poetry(ctx, f"run openapi-generator-cli generate {opts}")
