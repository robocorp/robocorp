from pathlib import Path
from invoke import task
from devutils.invoke_utils import build_common_tasks

CURDIR = Path(__file__).absolute().parent


globals().update(build_common_tasks(CURDIR, "robocorp._meta"))


@task
def update_deps(ctx):
    """Update all dependencies to match current versions"""
    import tomlkit

    pyproject = CURDIR / "pyproject.toml"
    contents = tomlkit.loads(pyproject.read_text())
    dependencies = contents["tool"]["poetry"]["dependencies"]

    for name, version in list(dependencies.items()):
        if name.startswith("robocorp-"):
            dep_name = name[len("robocorp-"):]
            dep_pyproject = CURDIR.parent / dep_name / "pyproject.toml"
            dep_contents = tomlkit.loads(dep_pyproject.read_text())
            dep_version = dep_contents["tool"]["poetry"]["version"]
            if version != dep_version:
                print(f"Updating {name}: {version} -> {dep_version}")
                dependencies[name] = dep_version

    pyproject.write_text(tomlkit.dumps(contents))
