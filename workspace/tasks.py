from pathlib import Path

from invoke import task

from devutils.invoke_utils import build_common_tasks


globals().update(
    build_common_tasks(Path(__file__).absolute().parent, "robocorp.storage")
)

OPENAPI_JSON = "https://robocorp.com/api/openapi.json"
OPENAPI_CONFIG = "openapiconf.yaml"


@task
def generate_api_client(ctx, minimal_update: bool = True, dry_run: bool = False):
    """Generate a Python OpenAPI client over the new Robocorp API."""
    opts_list = [
        f"-i {OPENAPI_JSON}",
        f"-c {OPENAPI_CONFIG}",
        "--skip-validate-spec"
    ]
    if minimal_update:
        opts_list.append("--minimal-update")
    if dry_run:
        opts_list.append("--dry-run")
    opts = " ".join(opts_list)
    poetry(f"run openapi-generator-cli generate -g python -o . {opts}")
