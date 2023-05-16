import os
from pathlib import Path
import pytest
from typing import Union
import subprocess


def run_in_rcc(rcc_loc: str, cwd: Union[str, Path], case_name: str, add_to_env: dict):
    env = os.environ.copy()
    env.pop("PYTHONPATH", "")
    env.pop("PYTHONHOME", "")
    env.pop("VIRTUAL_ENV", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"

    env["CASE_NAME"] = case_name
    env.update(add_to_env)

    completed_process = subprocess.run(
        [rcc_loc, "task", "run"], cwd=cwd, stdout=subprocess.PIPE, env=env
    )

    if completed_process.returncode != 0:
        raise AssertionError(
            f"Expected command to be run successfully. Result: {completed_process.returncode}.\n{completed_process}\nStdout:\n{completed_process.stdout.decode('utf-8')}\n"
        )
    return completed_process


def case_task_and_element() -> str:
    from robocorp import log
    from robocorp.log import setup_auto_logging
    from io import StringIO
    from robocorp_log_tests._resources import check
    from imp import reload

    s = StringIO()

    def on_write(msg):
        s.write(msg)

    with setup_auto_logging():
        check = reload(check)
        with log.add_in_memory_log_output(
            on_write,
        ):
            log.start_run("Robot1")
            log.start_task("Simple Task", "task_mod", __file__, 0)

            check.some_method()

            log.end_task("Simple Task", "task_mod", "PASS", "Ok")
            log.end_run("Robot1", "PASS")

    return s.getvalue()


case_names = ["case_task_and_element"]


# Can be used to regenerate the cases.
@pytest.mark.parametrize("case_name", case_names)
def _test_gen_base_cases(str_regression, case_name, datadir):
    create_case = globals()[case_name]
    str_regression.check(create_case(), basename=case_name)


@pytest.mark.parametrize("case_name", case_names)
def test_react_integrated(
    rcc_loc: str,
    path_for_output_view_react_tests_robo: Path,
    run_integration_tests_flag,
    datadir,
    case_name,
):
    """
    Note: this test will run the tests in:
    log/output-react/test_view_integrated_react
    """

    if not run_integration_tests_flag:
        pytest.skip(f"Disabled (not running integration tests).")

    tasks_py = path_for_output_view_react_tests_robo / "tasks.py"
    assert tasks_py.exists()
    completed_process = run_in_rcc(
        rcc_loc,
        path_for_output_view_react_tests_robo,
        case_name,
        {"PYTEST_DATADIR": str(datadir)},
    )
    stdout = completed_process.stdout.decode("utf-8")
    assert f"Running: {case_name}" in stdout or f"Running task: {case_name}" in stdout
