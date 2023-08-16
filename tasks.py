import subprocess
from pathlib import Path

import invoke
from invoke import task

CURDIR: Path = Path(__file__).absolute().parent


@task
def poetry_lock(ctx: invoke.Context) -> None:
    """Runs 'poetry lock' on all projects with a pyproject.toml."""
    for project_dir in _iter_project_dirs():
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

    for project_dir in _iter_project_dirs():
        if project_dir.name in ignored:
            continue

        subprocess.check_call(["poetry", "lock"], cwd=project_dir)
        subprocess.check_call(["poetry", "install"], cwd=project_dir)
        subprocess.check_call(["poetry", "run", "invoke", "docs"], cwd=project_dir)


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
            print(f"Package '{name}' version mismatch: {current} != {remote}")
            ok = False

    if ok:
        print("All packages up-to-date")
    else:
        raise invoke.Exit(code=1)


def _iter_project_dirs():
    for path in CURDIR.iterdir():
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
