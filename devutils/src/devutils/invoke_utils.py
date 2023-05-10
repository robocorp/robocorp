from invoke import task
import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Iterator, List


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


def get_tag(tag_prefix: str) -> str:
    """
    Args:
        tag_prefix: The tag prefix to match (i.e.: "robocorp-tasks")
    """
    import subprocess

    # i.e.: Gets the last tagged version
    cmd = f"git describe --tags --abbrev=0 --match {tag_prefix}*".split()
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = popen.communicate()

    # Something as: b'robocorp-tasks-0.0.1'
    return stdout.decode("utf-8").strip()


def get_all_tags(tag_prefix: str) -> List[str]:
    import subprocess

    cmd = "git tag".split()
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = popen.communicate()

    found = stdout.decode("utf-8").strip()
    return [x for x in found.splitlines() if x.startswith(tag_prefix)]


def build_common_tasks(root: Path, package_name: str):
    """
    Args:
        root: The path to the package root (i.e.: /tasks in the repo)
        package_name: The name of the python package (i.e.: robocorp.tasks)
    """

    # The tag for releases should be `robocorp-tasks-{version}`
    # i.e.: robocorp-tasks-0.1.1
    # Here we just want the prefix.
    tag_prefix = package_name.replace(".", "-")

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

    @task
    def check_tag_version(ctx):
        """
        Checks if the current tag matches the latest version (exits with 1 if it
        does not match and with 0 if it does match).
        """
        import importlib

        mod = importlib.import_module(package_name)

        tag = get_tag(tag_prefix)
        version = tag[tag.rfind("-") + 1 :]

        if mod.__version__ == version:
            sys.stderr.write(f"Version matches ({version}) (exit(0))\n")
            sys.exit(0)
        else:
            sys.stderr.write(
                f"Version does not match ({tag_prefix}: {mod.__version__} != repo tag: {version}).\nTags:{get_all_tags(tag_prefix)}\n(exit(1))\n"
            )
            sys.exit(1)

    @task
    def set_version_in_deps(ctx, version):
        """
        Sets a new version of this project in the project dependencies.
        """
        root_pyproject = root / "pyproject.toml"
        assert root_pyproject.exists(), f"Expected {root_pyproject} to exist."

        all_pyprojects = list(collect_deps_pyprojects(root_pyproject))
        all_pyprojects.append(root_pyproject)

    @task
    def set_version(ctx, version):
        """
        Sets a new version for the project in all the needed files.
        """
        import os.path

        def _fix_contents_version(contents, version):
            import re

            contents = re.sub(
                r"(version\s*=\s*)\"\d+\.\d+\.\d+", r'\1"%s' % (version,), contents
            )
            contents = re.sub(
                r"(__version__\s*=\s*)\"\d+\.\d+\.\d+", r'\1"%s' % (version,), contents
            )
            contents = re.sub(
                r"(\"version\"\s*:\s*)\"\d+\.\d+\.\d+", r'\1"%s' % (version,), contents
            )

            return contents

        def _fix_robocorp_tasks_contents_version_in_poetry(contents, version):
            import re

            contents = re.sub(
                r"(robocorp-tasks\s*=\s*)\"\^?\d+\.\d+\.\d+",
                r'\1"^%s' % (version,),
                contents,
            )
            return contents

        def update_version(version, filepath, fix_func=_fix_contents_version):
            with open(filepath, "r") as stream:
                contents = stream.read()

            new_contents = fix_func(contents, version)
            if contents != new_contents:
                print("Changed: ", filepath)
                with open(filepath, "w") as stream:
                    stream.write(new_contents)

        # Update version in current project pyproject.toml
        update_version(version, "pyproject.toml")

        # Update version in current project __init__.py
        parts = [".", "src"]
        parts.extend(package_name.split("."))
        parts.append("__init__.py")
        update_version(version, os.path.join(*parts))

    return locals()
