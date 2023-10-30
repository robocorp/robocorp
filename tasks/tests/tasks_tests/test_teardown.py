import subprocess
import typing
from typing import Dict, Optional

import pytest


@pytest.mark.parametrize("arg", ["argument", "environment_var"])
def test_neverending_teardown(datadir, arg) -> None:
    from devutils.fixtures import robocorp_tasks_run

    cmdline = [
        "run",
        "--console-colors=plain",
    ]
    additional_env: Optional[Dict[str, str]] = None

    if arg == "argument":
        cmdline.extend(
            (
                "--teardown-dump-threads-timeout=0.5",
                "--teardown-interrupt-timeout=1",
            )
        )
    else:
        additional_env = {
            "RC_TEARDOWN_DUMP_THREADS_TIMEOUT": "0.5",
            "RC_TEARDOWN_INTERRUPT_TIMEOUT": "1",
        }
    result = robocorp_tasks_run(
        cmdline,
        returncode="error",
        cwd=str(datadir / "neverending"),
        additional_env=additional_env,
    )
    stderr = result.stderr.decode("utf-8")

    assert stderr.count("= Thread Dump =") == 2


@pytest.mark.parametrize("arg", ["argument", "environment_var"])
def test_neverending_teardown_just_interrupt(datadir, arg) -> None:
    from devutils.fixtures import robocorp_tasks_run

    cmdline = [
        "run",
        "--console-colors=plain",
    ]
    additional_env: Optional[Dict[str, str]] = None

    if arg == "argument":
        cmdline.extend(
            (
                "--teardown-dump-threads-timeout=0",
                "--teardown-interrupt-timeout=1",
            )
        )
    else:
        additional_env = {
            "RC_TEARDOWN_DUMP_THREADS_TIMEOUT": "0",
            "RC_TEARDOWN_INTERRUPT_TIMEOUT": "1",
        }
    result = robocorp_tasks_run(
        cmdline,
        returncode="error",
        cwd=str(datadir / "neverending"),
        additional_env=additional_env,
    )
    stderr = result.stderr.decode("utf-8")

    assert stderr.count("= Thread Dump =") == 1


@pytest.mark.parametrize("arg", ["argument", "environment_var"])
def test_neverending_teardown_just_dump_threads(datadir, arg) -> None:
    from devutils.fixtures import robocorp_tasks_run

    cmdline = [
        "run",
        "--console-colors=plain",
    ]

    additional_env: Optional[Dict[str, str]] = None

    if arg == "argument":
        cmdline.extend(("--teardown-dump-threads-timeout=.5",))
    else:
        additional_env = {
            "RC_TEARDOWN_DUMP_THREADS_TIMEOUT": "0.5",
        }
    with pytest.raises(subprocess.TimeoutExpired) as e:
        robocorp_tasks_run(
            cmdline,
            returncode="error",
            cwd=str(datadir / "neverending"),
            additional_env=additional_env,
            timeout=2,
        )
    stderr_bytes: bytes = typing.cast(bytes, e.value.stderr)
    stderr = stderr_bytes.decode("utf-8")

    assert stderr.count("= Thread Dump =") == 1
