import os
from pathlib import Path
import pytest
from typing import Union, Optional
import subprocess


def run_in_rcc(
    rcc_loc: str,
    cwd: Union[str, Path],
    case_name: str,
    add_to_env: Optional[dict] = None,
):
    env = os.environ.copy()
    env.pop("PYTHONPATH", "")
    env.pop("PYTHONHOME", "")
    env.pop("VIRTUAL_ENV", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"

    env["CASE_NAME"] = case_name
    if add_to_env:
        env.update(add_to_env)

    completed_process = subprocess.run(
        [rcc_loc, "task", "run", "-t", case_name],
        cwd=cwd,
        stdout=subprocess.PIPE,
        env=env,
    )

    if completed_process.returncode != 0:
        raise AssertionError(
            f"Expected command to be run successfully. Result: {completed_process.returncode}.\n{completed_process}\nStdout:\n{completed_process.stdout.decode('utf-8')}\n"
        )
    return completed_process


case_names = [
    "case_task_and_element",
    "case_failure",
    "case_generators",
]


@pytest.mark.parametrize("case_name", case_names)
def test_react_integrated(
    rcc_loc: str,
    path_for_output_view_react_tests_robo: Path,
    run_integration_tests_flag,
    case_name,
):
    """
    Note: this test will run the tests in:
    log/output-react/test_view_integrated_react

    Using the scenarios at:

    tasks/tests/tasks_tests/test_create_scenarios
    """

    if not run_integration_tests_flag:
        pytest.skip(f"Disabled (not running integration tests).")

    tasks_py = path_for_output_view_react_tests_robo / "tasks.py"
    assert tasks_py.exists()
    completed_process = run_in_rcc(
        rcc_loc,
        path_for_output_view_react_tests_robo,
        case_name,
    )
    stdout = completed_process.stdout.decode("utf-8")
    assert f"Running: {case_name}" in stdout or f"Running task: {case_name}" in stdout
