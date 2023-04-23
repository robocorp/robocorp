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
    subprocess.check_call([str(rcc_loc)] + "task run --trace".split(), cwd=cwd, env=env)


def test_rpa_challenge_works(rcc_loc: Path, examples_dir: Path):
    from robocorp.log import verify_log_messages_from_log_html

    matrix_name = os.environ.get("GITHUB_ACTIONS_MATRIX_NAME")
    if matrix_name:
        if "logindev" not in matrix_name:
            pytest.skip(f"Disabled for matrix name: {matrix_name}")

    rpa_challenge_dir = examples_dir / "rpa-challenge-rcc"
    assert rpa_challenge_dir.exists()
    output_dir = rpa_challenge_dir / "output"
    log_html = output_dir / "log.html"

    if log_html.exists():
        os.remove(log_html)

    run_in_rcc(rcc_loc, rpa_challenge_dir)

    if not log_html.exists():
        raise AssertionError(f"Expected: {log_html} to exist.")

    verify_log_messages_from_log_html(
        log_html, [{"message_type": "SE", "name": "start_the_challenge"}]
    )

    if False:
        import webbrowser

        webbrowser.open(log_html.as_uri())
