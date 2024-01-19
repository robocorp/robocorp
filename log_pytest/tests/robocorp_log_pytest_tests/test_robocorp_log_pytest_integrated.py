import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


def run_pytest(
    cmdline, returncode, cwd=None, additional_env: Optional[Dict[str, str]] = None
):
    cp = os.environ.copy()
    cp["PYTHONPATH"] = os.pathsep.join([x for x in sys.path if x])
    if additional_env:
        cp.update(additional_env)
    args = [sys.executable, "-m", "pytest"] + cmdline
    result = subprocess.run(args, capture_output=True, env=cp, cwd=cwd)
    if result.returncode != returncode:
        env_str = "\n".join(str(x) for x in sorted(cp.items()))

        raise AssertionError(
            f"""Expected returncode: {returncode}. Found: {result.returncode}.
=== stdout:
{result.stdout.decode('utf-8')}

=== stderr:
{result.stderr.decode('utf-8')}

=== Env:
{env_str}

=== Args:
{args}

"""
        )
    return result


def test_integrated(datadir, str_regression) -> None:
    from robocorp.log._log_formatting import pretty_format_logs_from_log_html

    run_pytest(
        [
            f"--robocorp-log-output={datadir}/outputdir",
            "--robocorp-log-html-name=final_log.html",
            "--robocorp-log-max-files=1000",
            "--robocorp-log-max-file-size=10kb",
            str(datadir),
        ],
        returncode=1,
        cwd=str(datadir),
    )

    output_dir: Path = Path(str(datadir)) / "outputdir"
    robolog_files = list(output_dir.glob("*.robolog"))
    assert len(robolog_files) > 1
    log_html = output_dir / "final_log.html"
    str_regression.check(
        pretty_format_logs_from_log_html(log_html, show_restarts=False)
    )
