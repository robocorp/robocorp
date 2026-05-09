import os
from pathlib import Path

from invoke import task

from devutils.invoke_utils import build_common_tasks


globals().update(
    build_common_tasks(Path(__file__).absolute().parent, "robocorp.storage")
)

OPENAPI_JSON = "https://robocorp.com/api/openapi.json"
TYPES_MAPPING = {
    "Next": "Optional[StrictStr]",
    "HasMore": "StrictBool",
}


@task
def generate_api_client(ctx, minimal_update: bool = True, dry_run: bool = False):
    """Generate a Python OpenAPI client over the new Robocorp API."""
    exe_dir = Path("bin")
    os.environ["PYTHON_POST_PROCESS_FILE"] = f"python {exe_dir / 'post-process-module.py'}"
    types_mapping = ",".join(
        [f"{key}={value}" for key, value in TYPES_MAPPING.items()]
    )
    opts_list = [
        "-g python",
        f"-i {OPENAPI_JSON}",
        "-c openapiconf.yaml",
        "--skip-validate-spec",
        "-o src",
        "-t templates",
        f"--type-mappings {types_mapping}",
        "--enable-post-process-file",
    ]
    if minimal_update:
        opts_list.append("--minimal-update")
    if dry_run:
        opts_list.append("--dry-run")
    opts = " ".join(opts_list)
    # NOTE(cmin764, 07 Nov 2023): We're using the latest "openapi-generator-cli" tool
    #  pre-compiled and under our control. (as the one provided by PyPI is obsolete)
    openapi = exe_dir / "openapi-generator-cli.jar"
    poetry(ctx, f"run java -jar {openapi} generate {opts}")
