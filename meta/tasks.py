from pathlib import Path
from invoke import task
from devutils.invoke_utils import build_common_tasks

CURDIR = Path(__file__).absolute().parent


globals().update(
    build_common_tasks(
        root=CURDIR,
        package_name="robocorp._meta",
        tag_prefix="robocorp",
    )
)


@task
def update(ctx):
    """Update all dependencies to match current versions"""
    import tomlkit

    pyproject = CURDIR / "pyproject.toml"
    contents = tomlkit.loads(pyproject.read_text())
    dependencies = contents["tool"]["poetry"]["dependencies"]

    for name, version in list(dependencies.items()):
        if name.startswith("robocorp-"):
            dep_name = name[len("robocorp-") :]
            dep_pyproject = CURDIR.parent / dep_name / "pyproject.toml"
            dep_contents = tomlkit.loads(dep_pyproject.read_text())
            dep_version = dep_contents["tool"]["poetry"]["version"]
            if version != dep_version:
                print(f"Updating {name}: {version} -> {dep_version}")
                dependencies[name] = dep_version

    pyproject.write_text(tomlkit.dumps(contents))


@task
def outdated(ctx):
    """Check if dependencies in metapackage are outdated"""
    import sys
    import tomlkit

    pyproject = CURDIR / "pyproject.toml"
    contents = tomlkit.loads(pyproject.read_text())
    dependencies = contents["tool"]["poetry"]["dependencies"]

    errors = []
    for name, version in list(dependencies.items()):
        if not name.startswith("robocorp-"):
            continue

        print(f"Checking package: {name}")
        dep_version = _fetch_version(name)
        if version != dep_version:
            errors.append(f"Outdated version for '{name}': {version} != {dep_version}")

    if errors:
        for err in errors:
            print(err)
        sys.exit(1)


def _fetch_version(name):
    import json
    import urllib.request

    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json") as response:
        metadata = json.loads(response.read())

    latest = max(metadata["releases"].keys(), key=_to_semver)
    return latest


def _to_semver(version):
    import re

    match = re.search(r"(\d+)\.(\d+)\.(\d+)", version)
    assert match is not None, f"Not a valid version: {version}"
    major, minor, micro = match.groups()
    return int(major), int(minor), int(micro)
