from invoke import task
import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Iterator


class RoundtripPyProject:
    def __init__(self, pyproject: Path):
        self.pyproject = pyproject
        self.original = pyproject.read_bytes()

        self.poetry_lock = pyproject.parent / "poetry.lock"
        self.poetry_lock_original = self.poetry_lock.read_bytes()

    @contextmanager
    def update(self):
        import tomlkit  # allows roundtrip of toml files

        contents = tomlkit.loads(self.original.decode("utf-8"))
        yield contents
        new = tomlkit.dumps(contents).encode("utf-8")
        self.pyproject.write_bytes(new)

    def restore(self):
        self.pyproject.write_bytes(self.original)
        self.poetry_lock.write_bytes(self.poetry_lock_original)


def collect_deps_pyprojects(root_pyproject: Path, found=None) -> Iterator[Path]:
    if found is None:
        found = set()

    import tomlkit  # allows roundtrip of toml files

    contents: dict = tomlkit.loads(root_pyproject.read_bytes().decode("utf-8"))
    dependencies = contents["tool"]["poetry"]["dependencies"]
    for key in dependencies:
        if key.startswith("robocorp-"):
            dep_name = key[len("robocorp-") :]
            dep_pyproject = root_pyproject.parent.parent / dep_name / "pyproject.toml"
            assert dep_pyproject.exists(), f"Expected {dep_pyproject} to exist."
            if dep_pyproject not in found:
                found.add(dep_pyproject)
                yield dep_pyproject
                yield from collect_deps_pyprojects(dep_pyproject, found)


def build_common_tasks(root, package_name):
    DIST = root / "dist"

    def poetry(ctx, *parts):
        import os

        os.chdir(root)
        args = " ".join(str(part) for part in parts)
        ctx.run(f"poetry {args}", pty=sys.platform != "win32", echo=True)

    @task
    def install(ctx):
        """Install dependencies"""
        poetry(ctx, "install")

    @task
    def devinstall(ctx):
        """Install dependencies with deps in dev mode"""
        root_pyproject = root / "pyproject.toml"
        assert root_pyproject.exists(), f"Expected {root_pyproject} to exist."

        all_pyprojects = list(collect_deps_pyprojects(root_pyproject))
        all_pyprojects.append(root_pyproject)

        roundtrips = []
        try:
            for pyproject in all_pyprojects:
                roundtrip_py_project = RoundtripPyProject(pyproject)
                roundtrips.append(roundtrip_py_project)
                with roundtrip_py_project.update() as contents:
                    dependencies = contents["tool"]["poetry"]["dependencies"]

                    for key, value in tuple(dependencies.items()):
                        # Changes something as:
                        # robocorp-log = "0.1.0"
                        # to:
                        # robocorp-log = {path = "../log/", develop = true}
                        if key.startswith("robocorp-"):
                            name = key[len("robocorp-") :]
                            value = dict(path=f"../{name}/", develop=True)
                            dependencies[key] = value

            poetry(ctx, "lock --no-update")
            poetry(ctx, "install")
        finally:
            for roundtrip in roundtrips:
                roundtrip.restore()

    @task
    def lint(ctx):
        """Run static analysis and formatting checks"""
        poetry(ctx, f"run ruff src tests")
        poetry(ctx, f"run black --check src tests")
        poetry(ctx, f"run isort --check src tests")

    @task
    def typecheck(ctx):
        """Type check code"""
        poetry(
            ctx,
            f"run mypy --follow-imports=silent --show-column-numbers --namespace-packages --explicit-package-bases src tests",
        )

    @task
    def pretty(ctx):
        """Auto-format code and sort imports"""
        poetry(ctx, f"run black src tests")
        poetry(ctx, f"run isort src tests")

    @task
    def test(ctx):
        """Run unittests"""
        poetry(ctx, f"run pytest")

    @task
    def build(ctx):
        """Build distributable .tar.gz and .wheel files"""
        poetry(ctx, "build")

    @task
    def publish(ctx):
        """Publish package to PyPI"""
        for file in DIST.glob("*"):
            print(f"Removing: {file}")
            file.unlink()

        poetry(ctx, "publish", "--build")

    @task
    def docs(ctx):
        """Build API documentation"""
        poetry(
            ctx,
            "run lazydocs",
            "--overview-file README.md",
            "--remove-package-prefix",
            package_name,
        )

    return locals()
