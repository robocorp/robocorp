import shlex
import subprocess
import sys
from pathlib import Path
from typing import Optional

import invoke
from invoke import call, task


ROOT: Path = Path(__file__).absolute().parent

DOCS_IGNORE = ["devutils"]
if sys.platform != "win32":
    DOCS_IGNORE.append("windows")


@task
def install(
    ctx: invoke.Context,
    update: bool = False,
    verbose: bool = False,
    skip: Optional[list[str]] = None,
) -> None:
    """Refresh/Install all Poetry-based projects' environments.

    Args:
        update: Whether to update the dependencies or just installing them.
        verbose: Whether to run in verbose mode.
        skip: List of project directories to skip.

    Note:
        Can't use threads to speed it up. (Poetry or pip will just fail)
    """
    for project_dir in _iter_project_dirs():
        project_name = project_dir.name
        if skip and project_name in skip:
            print(f"Skipping project {project_name!r}.")
            continue

        inv_cmd, poetry_cmd = "invoke install", "poetry install"
        if update:
            inv_cmd += " -u"
            poetry_cmd = poetry_cmd.replace("install", "update")
        if verbose:
            inv_cmd += " -v"
            poetry_cmd += " -vv"

        cmd = inv_cmd if (project_dir / "tasks.py").exists() else poetry_cmd
        subprocess.check_call(shlex.split(cmd), cwd=project_dir)


@task(pre=[call(install, skip=DOCS_IGNORE)])
def docs(ctx: invoke.Context) -> None:
    """Regenerate documentation for each library."""
    cmd = "invoke docs"
    for project_dir in _iter_project_dirs():
        if project_dir.name in DOCS_IGNORE:
            continue

        print(f"Generating docs in {str(project_dir)!r}...")
        subprocess.check_call(shlex.split(cmd), cwd=project_dir)


@task
def unreleased(ctx: invoke.Context) -> None:
    """Compare current branch to PyPI."""
    import tomlkit

    ignored = [
        "devutils",
        "integration_tests",
    ]

    ok = True
    for project_dir in _iter_project_dirs():
        if project_dir.name in ignored:
            continue

        pyproject = project_dir / "pyproject.toml"
        contents = tomlkit.loads(pyproject.read_text())
        poetry = contents["tool"]["poetry"]

        name = poetry["name"]
        current = poetry["version"]
        remote = _pypi_version(name)

        if current != remote:
            print(f"Package {name!r} version mismatch: {current} != {remote}")
            ok = False

    if ok:
        print("All packages are up-to-date!")
    else:
        raise invoke.Exit(code=1)


def _iter_project_dirs():
    for path in ROOT.iterdir():
        if path.is_dir():
            if (path / "pyproject.toml").exists():
                yield path


def _pypi_version(name: str) -> str:
    import json
    import urllib.request
    import semver

    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json") as response:
        metadata = json.loads(response.read())

    latest = max(metadata["releases"].keys(), key=semver.Version.parse)
    return latest
