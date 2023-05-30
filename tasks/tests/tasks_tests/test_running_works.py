import os
from pathlib import Path

import pytest


def test_rpa_challenge_works(rcc_loc: Path, resources_dir: Path):
    from devutils.fixtures import run_in_rcc
    from robocorp.log import verify_log_messages_from_log_html

    matrix_name = os.environ.get("GITHUB_ACTIONS_MATRIX_NAME")
    if matrix_name:
        if "logindev" not in matrix_name:
            pytest.skip(f"Disabled for matrix name: {matrix_name}")

    rpa_challenge_dir = resources_dir / "rpa-challenge"
    assert rpa_challenge_dir.exists()
    output_dir = rpa_challenge_dir / "output"
    log_html = output_dir / "log.html"

    if log_html.exists():
        os.remove(log_html)

    run_in_rcc(rcc_loc, rpa_challenge_dir)

    if not log_html.exists():
        raise AssertionError(f"Expected: {log_html} to exist.")

    verify_log_messages_from_log_html(
        log_html, [{"message_type": "SE", "name": "solve_challenge"}]
    )

    if False:
        import webbrowser

        webbrowser.open(log_html.as_uri())
