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


def gen_case1(path_for_tests_robot: Path, tmpdir: Path):
    from robocorp import log

    resources_path = path_for_tests_robot / "_resources"
    case1: Path = resources_path / "case1.robolog"
    with log.add_log_output(
        tmpdir,
    ):
        log.start_run("Robot1")
        log.start_task("Simple Task", "task_mod", __file__, 0)

        log.end_task("Simple Task", "task_mod", "PASS", "Ok")
        log.end_run("Robot1", "PASS")

    dest: Path = tmpdir / "output.robolog"
    case1.write_bytes(dest.read_bytes())


def gen_case4(path_for_tests_robot: Path, tmpdir: Path):
    from robocorp import log
    from robocorp.log import setup_auto_logging

    resources_path = path_for_tests_robot / "_resources"
    case1: Path = resources_path / "case4.robolog"
    with setup_auto_logging():
        with log.add_log_output(
            tmpdir,
        ):
            log.start_run("Robot1")
            log.start_task("Simple Task", "task_mod", __file__, 0)

            from . import _help_screenshot

            _help_screenshot.screenshot(True)

            log.end_task("Simple Task", "task_mod", "PASS", "Ok")
            log.end_run("Robot1", "PASS")

    dest: Path = tmpdir / "output.robolog"
    case1.write_bytes(dest.read_bytes())


def test_output_view_integrated(rcc_loc: str, path_for_tests_robot: Path, tmpdir):
    matrix_name = os.environ.get("GITHUB_ACTIONS_MATRIX_NAME")
    if matrix_name:
        if "outviewintegrationtests" not in matrix_name:
            pytest.skip(f"Disabled for matrix name: {matrix_name}")

    # gen_case1(path_for_tests_robot, Path(str(tmpdir)))
    # case2 == case1 but with additional restart variant before ending:
    # RR a|0.016
    # RT b|0.016
    # case3 == case2 but removing SR/ST
    # RR a|0.016
    # RT b|0.016
    # gen_case4(path_for_tests_robot, Path(str(tmpdir)))

    p = Path(__file__)
    p = p.absolute()
    logging_root: Path = p.parent.parent.parent
    test_index = logging_root / "output-webview" / "dist-test" / "index.html"
    if not test_index.exists():
        raise AssertionError(
            f"{test_index} does not exist. Generate with 'yarn build-test' in the 'output-webview' folder."
        )

    robot_yaml = path_for_tests_robot / "robot.yaml"
    assert robot_yaml.exists()
    run_in_rcc(rcc_loc, str(path_for_tests_robot))
