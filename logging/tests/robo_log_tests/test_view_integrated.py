import os
from pathlib import Path
import pytest


def run_in_rcc(rcc_loc: str, cwd: str):
    import subprocess

    env = os.environ.copy()
    env.pop("PYTHONPATH", "")
    env.pop("PYTHONHOME", "")
    env.pop("VIRTUAL_ENV", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    subprocess.check_call([rcc_loc] + "task run".split(), cwd=cwd, env=env)


def test_output_view_integrated(rcc_loc: str, path_for_tests_robot: Path):
    matrix_name = os.environ.get("GITHUB_ACTIONS_MATRIX_NAME")
    if matrix_name:
        if "outviewintegrationtests" not in matrix_name:
            pytest.skip(f"Disabled for matrix name: {matrix_name}")

    robot_yaml = path_for_tests_robot / "robot.yaml"
    assert robot_yaml.exists()
    run_in_rcc(rcc_loc, str(path_for_tests_robot))
