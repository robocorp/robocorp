import os
import subprocess
from pathlib import Path
from typing import Optional, Union

import pytest

from integration_tests import _case_names


def _run_in_rcc(
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
            "Expected command to be run successfully. "
            f"Result: {completed_process.returncode}.\n"
            f"{completed_process}\nStdout:\n"
            f"{completed_process.stdout.decode('utf-8')}\n"
        )
    return completed_process


@pytest.mark.parametrize("case_name", _case_names.case_names)
def test_react_integrated(
    rcc_loc: str,
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
        pytest.skip("Disabled (not running integration tests).")

    path_with_tasks = Path(__file__).parent / "test_view_integrated_react"

    tasks_py = path_with_tasks / "tasks.py"
    assert tasks_py.exists()
    completed_process = _run_in_rcc(
        rcc_loc,
        path_with_tasks,
        case_name,
    )
    stdout = completed_process.stdout.decode("utf-8")
    assert f"Running: {case_name}" in stdout or f"Running task: {case_name}" in stdout
