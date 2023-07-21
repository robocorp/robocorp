import subprocess
from pathlib import Path

import invoke
from invoke import task

CURDIR: Path = Path(__file__).absolute().parent


def iter_project_dirs():
    for d in CURDIR.iterdir():
        if d.is_dir():
            if (d / "pyproject.toml").exists():
                yield d


@task
def poetry_lock(ctx: invoke.Context) -> None:
    """Runs 'poetry lock' on all projects with a pyproject.toml."""
    for project_dir in iter_project_dirs():
        # Note: can't use threads to speed it up. poetry (or pip) just fail...
        subprocess.check_call(["poetry", "lock"], cwd=project_dir)


@task
def docs(ctx: invoke.Context) -> None:
    """Regenerate documentation for each library."""
    ignored = [
        "devutils",
        "integration_tests",
        "meta",
    ]

    for project_dir in iter_project_dirs():
        if project_dir.name in ignored:
            continue

        subprocess.check_call(["poetry", "install"], cwd=project_dir)
        subprocess.check_call(["poetry", "run", "invoke", "docs"], cwd=project_dir)
