import os
import sys
from pathlib import Path


def test_binary_build():
    import subprocess

    # Checks if the versions in pyoxidizer are correct
    # and if the binary selftest works properly
    CURDIR = Path(__file__).absolute()
    action_server_dir = CURDIR.parent.parent.parent
    blz_file = action_server_dir / "build-binary" / "pyoxidizer.bzl"
    assert blz_file.exists()

    # TODO: Remove when https://github.com/robocorp/robocorp/pull/322 is
    # added as it adds the dep to the dev deps (not adding it in this PR
    # to avoid conflicts).
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "pyoxidizer"],
    )

    before = blz_file.read_text().replace("\r\n", "\n").replace("\r", "\n")
    subprocess.check_call(
        [sys.executable, "-m", "invoke", "update-pyoxidizer-versions"],
        cwd=action_server_dir,
    )
    after = blz_file.read_text().replace("\r\n", "\n").replace("\r", "\n")

    if before != after:
        raise AssertionError(
            "inv update-pyoxidizer-versions must be run to update binary versions"
        )

    env = os.environ.copy()
    env.pop("PYTHONPATH", "")
    env.pop("PYTHONHOME", "")
    env.pop("VIRTUAL_ENV", "")
    env["RC_ACTION_SERVER_FORCE_DOWNLOAD_RCC"] = "True"
    env["RC_ACTION_SERVER_DO_SELFTEST"] = "True"
    env["PYTHONIOENCODING"] = "utf-8"

    subprocess.check_call(
        ["pyoxidizer", "run", "--release"],
        cwd=action_server_dir / "build-binary",
        env=env,
    )
