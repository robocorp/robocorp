import os
from pathlib import Path
import pytest


def run_in_rcc(rcc_loc: Path, cwd: Path):
    import subprocess

    env = os.environ.copy()
    env.pop("PYTHONPATH", "")
    env.pop("PYTHONHOME", "")
    env.pop("VIRTUAL_ENV", "")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    subprocess.check_call([str(rcc_loc)] + "task run".split(), cwd=cwd, env=env)


def test_rpa_challenge_works(rcc_loc: Path, examples_dir: Path):
    matrix_name = os.environ.get("GITHUB_ACTIONS_MATRIX_NAME")
    if matrix_name:
        if "logindev" not in matrix_name:
            pytest.skip(f"Disabled for matrix name: {matrix_name}")

    from robo_log import iter_decoded_log_format_from_log_html

    rpa_challenge_dir = examples_dir / "rpa-challenge-rcc"
    assert rpa_challenge_dir.exists()
    output_dir = rpa_challenge_dir / "output"
    log_html = output_dir / "log.html"

    if log_html.exists():
        os.remove(log_html)

    run_in_rcc(rcc_loc, rpa_challenge_dir)

    if not log_html.exists():
        raise AssertionError(f"Expected: {log_html} to exist.")

    log_messages = tuple(iter_decoded_log_format_from_log_html(log_html))
    for log_msg in log_messages:
        if log_msg["message_type"] == "SE" and log_msg["name"] == "start_the_challenge":
            break
    else:
        new_line = "\n"
        raise AssertionError(
            f"Did not find SE/some_method message. Found: {new_line.join(str(x) for x in log_messages)}"
        )
