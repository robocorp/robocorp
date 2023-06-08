import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List

from invoke import run, task


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

    def run(ctx, *cmd, **options):
        import os

        options.setdefault("pty", sys.platform != "win32")
        options.setdefault("echo", True)

        os.chdir(root)
        args = " ".join(str(c) for c in cmd)
        return ctx.run(args, **options)

    def poetry(ctx, *cmd):
        return run(ctx, "poetry", *cmd)

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
            "run mypy",
            "--follow-imports=silent",
            "--show-column-numbers",
            "--namespace-packages",
            "--explicit-package-bases",
            f"-p {package_name}",
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
    def make_release(ctx):
        """Create a release tag"""
        import importlib

        import semver

        result = run(ctx, "git rev-parse --abbrev-ref HEAD", hide=True)
        branch = result.stdout.strip()
        if branch != "master":
            sys.stderr.write(f"Not on master branch: {branch}\n")
            sys.exit(1)

        current_version = importlib.import_module(package_name).__version__

        previous_tag = get_tag(tag_prefix)
        previous_version = previous_tag.split("-")[-1]

        if not previous_version:
            print(f"No previous release for {package_name}")
        elif semver.compare(current_version, previous_version) <= 0:
            sys.stderr.write(
                f"Current version older/same than previous: {current_version} <= {previous_version}\n"
            )
            sys.exit(1)

        current_tag = f"{tag_prefix}-{current_version}"
        run(
            ctx,
            "git tag",
            "-a",
            current_tag,
            "-m",
            f'"Release {current_version} for {package_name}"',
            echo=True,
        )

        print(f"Trigger the release with: git push origin {current_tag}")

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
        """Sets a new version of this project in the project dependencies"""
        root_pyproject = root / "pyproject.toml"
        assert root_pyproject.exists(), f"Expected {root_pyproject} to exist."

        all_pyprojects = list(collect_deps_pyprojects(root_pyproject))
        all_pyprojects.append(root_pyproject)

    @task
    def set_version(ctx, version):
        """Sets a new version for the project in all the needed files"""
        import re
        from pathlib import Path

        version_patterns = (
            re.compile(r"(version\s*=\s*)\"\d+\.\d+\.\d+"),
            re.compile(r"(__version__\s*=\s*)\"\d+\.\d+\.\d+"),
            re.compile(r"(\"version\"\s*:\s*)\"\d+\.\d+\.\d+"),
        )

        def update_version(version, filepath):
            with open(filepath, "r") as stream:
                before = stream.read()

            after = before
            for pattern in version_patterns:
                after = re.sub(pattern, r'\1"%s' % (version,), after)

            if before != after:
                print("Changed: ", filepath)
                with open(filepath, "w") as stream:
                    stream.write(after)

        # Update version in current project pyproject.toml
        update_version(version, "pyproject.toml")

        # Update version in current project __init__.py
        package_path = package_name.split(".")
        init_file = Path(root, "src", *package_path, "__init__.py")
        update_version(version, init_file)

    return locals()
