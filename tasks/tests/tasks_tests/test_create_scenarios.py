from pathlib import Path

import pytest
from devutils.fixtures import run_in_rcc


def case_task_and_element(rcc_loc, resources_dir: Path) -> str:
    from imp import reload
    from io import StringIO

    from robocorp.log import setup_auto_logging
    from tasks_tests.resources import check

    from robocorp import log

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


def case_failure(rcc_loc: str, resources_dir: Path) -> str:
    gen_scenarios_dir = resources_dir / "gen-scenarios"
    assert gen_scenarios_dir.exists()
    run_in_rcc(
        Path(rcc_loc),
        cwd=gen_scenarios_dir,
        args=["-t", "case_failure"],
        expect_error=True,
    )
    robolog = gen_scenarios_dir / "output" / "output.robolog"
    assert robolog.exists()
    return robolog.read_bytes().decode("utf-8")


def case_log(rcc_loc: str, resources_dir: Path) -> str:
    gen_scenarios_dir = resources_dir / "gen-scenarios"
    assert gen_scenarios_dir.exists()
    run_in_rcc(
        Path(rcc_loc),
        cwd=gen_scenarios_dir,
        args=["-t", "case_log"],
    )
    robolog = gen_scenarios_dir / "output" / "output.robolog"
    assert robolog.exists()
    return robolog.read_bytes().decode("utf-8")


def case_generators(rcc_loc: str, resources_dir: Path) -> str:
    gen_scenarios_dir = resources_dir / "gen-scenarios"
    assert gen_scenarios_dir.exists()
    run_in_rcc(
        Path(rcc_loc),
        cwd=gen_scenarios_dir,
        args=["-t", "case_generators"],
    )
    robolog = gen_scenarios_dir / "output" / "output.robolog"
    assert robolog.exists()
    return robolog.read_bytes().decode("utf-8")


case_names = [
    "case_task_and_element",
    "case_failure",
    "case_generators",
    "case_log",
]


# Can be used to regenerate the cases.
@pytest.mark.parametrize("case_name", case_names)
def _test_gen_base_cases(str_regression, case_name, datadir, rcc_loc, resources_dir):
    create_case = globals()[case_name]
    results = create_case(rcc_loc, resources_dir).replace(r"\\", "/")
    str_regression.check(results, basename=case_name)
