from pathlib import Path

from devutils.invoke_utils import build_common_tasks
from invoke import task

CURDIR = Path(__file__).absolute().parent


globals().update(
    build_common_tasks(
        root=CURDIR,
        package_name="robocorp._meta",
        tag_prefix="robocorp",
    )
)

if False:
    # Forward declarations from invoke_utils so that static
    # analyzers understand it.
    def poetry(ctx, *cmd):
        raise RuntimeError("Defined in invoke_utils.")

    def set_version(ctx, version):
        raise RuntimeError("Defined in invoke_utils.")


@task
def update(ctx):
    """Update all dependencies to match current versions"""
    import tomlkit

    pyproject = CURDIR / "pyproject.toml"
    contents = tomlkit.loads(pyproject.read_text())
    dependencies = contents["tool"]["poetry"]["dependencies"]

    changes = []
    for name, version in list(dependencies.items()):
        if name.startswith("robocorp-"):
            dep_name = name[len("robocorp-") :]
            dep_pyproject = CURDIR.parent / dep_name / "pyproject.toml"
            dep_contents = tomlkit.loads(dep_pyproject.read_text())
            dep_version = f'^{dep_contents["tool"]["poetry"]["version"]}'
            if version != dep_version:
                print(f"Updating {name}: {version} -> {dep_version}")
                dependencies[name] = dep_version
                changes.append((version, dep_version))

    if not changes:
        print("Nothing to update")
        return

    pyproject.write_text(tomlkit.dumps(contents))

    meta_version = contents["tool"]["poetry"]["version"]
    meta_version = _bump_by_changes(meta_version, changes)
    print(f"New metapackage version: {meta_version}")
    set_version(ctx, meta_version)

    poetry(ctx, "lock")


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

    import semver

    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/json") as response:
        metadata = json.loads(response.read())

    latest = max(metadata["releases"].keys(), key=semver.Version.parse)
    return latest


def _bump_by_changes(version, changes):
    if version.startswith("^"):
        version = version[1:]

    import semver

    version = semver.Version.parse(version)
    major, minor, patch = False, False, False

    for before, after in changes:
        if before.startswith("^"):
            before = before[1:]

        if after.startswith("^"):
            after = after[1:]

        before = semver.Version.parse(before)
        after = semver.Version.parse(after)

        if after.major > before.major:
            major = True
        elif after.minor > before.minor:
            minor = True
        elif after.patch > before.patch:
            patch = True

    if major:
        return str(version.bump_major())
    elif minor:
        return str(version.bump_minor())
    elif patch:
        return str(version.bump_patch())

    raise RuntimeError("No version changes found")
