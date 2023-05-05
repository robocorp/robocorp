import os
from pathlib import Path
import pytest
from typing import Union
import subprocess


def run_in_rcc(rcc_loc: str, cwd: Union[str, Path]):
    import subprocess

    env = os.environ.copy()
    env.pop("PYTHONPATH", "")
    env.pop("PYTHONHOME", "")
    env.pop("VIRTUAL_ENV", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    subprocess.check_call([rcc_loc] + "task run".split(), cwd=cwd, env=env)


def run_in_robo(robo_loc: str, cwd: Union[str, Path]) -> subprocess.CompletedProcess:
    completed_process = subprocess.run(
        [robo_loc, "run"], cwd=cwd, stdout=subprocess.PIPE
    )

    if completed_process.returncode != 0:
        raise AssertionError(
            f"Expected command to be run successfully. Result: {completed_process.returncode}.\n{completed_process}\nStdout:\n{completed_process.stdout.decode('utf-8')}\n"
        )
    return completed_process


def gen_case1(path_for_output_view_tests: Path, tmpdir: Path):
    from robocorp import log

    resources_path = path_for_output_view_tests / "_resources"
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


def gen_case4(path_for_output_view_tests: Path, tmpdir: Path):
    from robocorp import log
    from robocorp.log import setup_auto_logging

    resources_path = path_for_output_view_tests / "_resources"
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


def test_output_view_integrated(
    rcc_loc: str, path_for_output_view_tests: Path, tmpdir, run_integration_tests_flag
):
    if not run_integration_tests_flag:
        pytest.skip(f"Disabled (not running integration tests).")

    # gen_case1(path_for_output_view_tests, Path(str(tmpdir)))
    # case2 == case1 but with additional restart variant before ending:
    # RR a|0.016
    # RT b|0.016
    # case3 == case2 but removing SR/ST
    # RR a|0.016
    # RT b|0.016
    # gen_case4(path_for_output_view_tests, Path(str(tmpdir)))

    p = Path(__file__)
    p = p.absolute()
    logging_root: Path = p.parent.parent.parent
    test_index = logging_root / "output-webview" / "dist-test" / "index.html"
    if not test_index.exists():
        raise AssertionError(
            f"{test_index} does not exist. Generate with 'yarn build-test' in the 'output-webview' folder."
        )

    robot_yaml = path_for_output_view_tests / "robot.yaml"
    assert robot_yaml.exists()
    run_in_rcc(rcc_loc, path_for_output_view_tests)


def test_output_view_integrated_robo(
    robo_loc: str, path_for_output_view_tests_robo: Path, run_integration_tests_flag
):
    if not run_integration_tests_flag:
        pytest.skip(f"Disabled (not running integration tests).")

    tasks_py = path_for_output_view_tests_robo / "tasks.py"
    assert tasks_py.exists()
    completed_process = run_in_robo(robo_loc, path_for_output_view_tests_robo)
    stdout = completed_process.stdout.decode("utf-8")
    assert "Running task: check_output_webview" in stdout
