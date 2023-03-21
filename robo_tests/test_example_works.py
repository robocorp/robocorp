import os
from pathlib import Path


def run_in_rcc(rcc_loc: Path, cwd: Path):
    import subprocess

    env = os.environ.copy()
    env.pop("PYTHONPATH", "")
    env.pop("PYTHONHOME", "")
    env.pop("VIRTUAL_ENV", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    subprocess.check_call(
        [str(rcc_loc)] + "task run robot.yaml".split(), cwd=cwd, env=env
    )


def test_rpa_challenge_works(rcc_loc: Path, examples_dir: Path):
    rpa_challenge_dir = examples_dir / "rpa-challenge"
    assert rpa_challenge_dir.exists()
    run_in_rcc(rcc_loc, rpa_challenge_dir)
