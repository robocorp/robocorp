import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
from contextlib import contextmanager
from datetime import datetime
from functools import lru_cache
from itertools import chain
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple, Union

from invoke import task

ROOT = Path(__file__).absolute().parent.parent.parent
REPOSITORY_URL = "https://github.com/robocorp/robocorp/tree/master/"


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
    # Get the last tagged version.
    cmd = f"git describe --tags --abbrev=0 --match {tag_prefix}-[0-9]*"
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    # Something like 'robocorp-tasks-0.0.1'
    return proc.stdout.strip()


def get_all_tags(tag_prefix: str) -> List[str]:
    cmd = "git tag"
    proc = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
    tags = proc.stdout.strip().splitlines()
    regex = re.compile(rf"{tag_prefix}-[\d.]+$")
    return [tag for tag in tags if regex.match(tag)]


def to_identifier(value: str) -> str:
    value = re.sub(r"[^\w\s_]", "", value.lower())
    value = re.sub(r"[_\s]+", "_", value).strip("_")
    return value


@lru_cache
def _use_conda() -> bool:
    """
    Determines whether conda should be used for the env.
    """
    use_conda_flag = os.environ.get("RC_USE_CONDA", "")
    if use_conda_flag:
        if use_conda_flag.lower() in ("1", "true"):
            return True
        if use_conda_flag.lower() in ("0", "false"):
            return False
        raise RuntimeError(
            f'Unrecognized value for "RC_USE_CONDA" env var: {use_conda_flag!r}.'
        )
    conda_exe = os.environ.get("CONDA_EXE")
    if not conda_exe:
        return False
    if Path(conda_exe).exists():
        return True
    return False


def _conda_env_name_to_conda_prefix() -> Dict[str, str]:
    ret = {}
    cmd = "conda env list"
    output = subprocess.check_output(shlex.split(cmd), encoding="utf-8")
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("#") or not line:
            continue
        try:
            name, prefix = line.split()
        except Exception:
            continue  # Not all lines have the name and prefix
        name = name.strip()
        ret[name] = prefix
    return ret


def _activated_conda_env() -> Optional[str]:
    if os.environ.get("CONDA_PREFIX"):
        return os.environ.get("CONDA_DEFAULT_ENV", "").strip()
    return None


def _env_in_conda(env_name) -> bool:
    """
    If the given environment name exists in conda, return True, otherwise False.

    :param env_name:
        The name of the env to check (example: 'robocorp-tasks').
    """
    return env_name in _conda_env_name_to_conda_prefix()


def build_common_tasks(
    root: Path,
    package_name: str,
    tag_prefix: Optional[str] = None,
    ruff_format_arguments: str = "",
    parallel_tests: bool = True,
    source_directories: Tuple[str, ...] = ("src", "tests"),
):
    """Builds the common tasks in every task.py file of the inheriting packages.

    Args:
        root: The path to the package root. (i.e.: ./tasks in the repo)
        package_name: The name of the python package. (i.e.: "robocorp.tasks")
        tag_prefix: Optional prefix for tags / PyPI package name.
        ruff_format_arguments: Pass extra options to the ruff formatting commands.
        parallel_tests: Runs tests in parallels. (enabled by default)
        source_directories: Default Python source directories.
    """
    if tag_prefix is None:
        # The tag for releases should be `robocorp-tasks-{version}`
        # i.e.: robocorp-tasks-0.1.1
        # Here we just want the prefix.
        tag_prefix = package_name.replace(".", "-")

    DIST = root / "dist"
    CONDA_ENV_NAME = package_name.replace(".", "-").replace("_", "-")
    TARGETS = " ".join(source_directories)
    RUFF_ARGS = f"--config {ROOT / 'ruff.toml'} {ruff_format_arguments}".strip()

    def run(ctx, *cmd, **options):
        options.setdefault("pty", sys.platform != "win32")
        options.setdefault("echo", True)

        os.chdir(root)
        args = " ".join(str(c) for c in cmd)
        return ctx.run(args, **options)

    def poetry(ctx, *cmd, verbose: bool = False):
        prefix = []
        if _use_conda():
            prefix.extend(["conda", "run", "--no-capture-output", "-n", CONDA_ENV_NAME])
        prefix.append("poetry")

        if verbose:
            prefix.append("-vv")

        return run(ctx, *prefix, *cmd)

    def _make_conda_env_if_needed():
        if _use_conda():
            if not _env_in_conda(CONDA_ENV_NAME):
                print(f"Conda env: {CONDA_ENV_NAME} not found. Creating now.")
                cmd = f"conda create -c conda-forge -n {CONDA_ENV_NAME} python=3.10 -y"
                subprocess.check_call(shlex.split(cmd))

    @task
    def install(
        ctx, local: Optional[str] = None, update: bool = False, verbose: bool = False
    ):
        """Optionally updates then also installs dependencies.

        This also supports specifying local dependencies installed in development mode
        through the `local` argument. Enable `verbose` to increase logging. Passing
        `-u` / `--update` will update the dependencies in the *.lock file first, then
        it will continue with the installation as usual.

        Args:
            local: A comma-separated list of local projects to install in develop mode.
            update: Whether to update the dependencies first.
            verbose: Whether to run in verbose mode.
        """
        _make_conda_env_if_needed()

        if update:
            poetry(ctx, "update", verbose=verbose)

        projects = (
            [package.replace("robocorp-", "") for package in local.split(",")]
            if local
            else None
        )
        if projects:
            with mark_as_develop_mode(projects):
                poetry(ctx, "lock --no-update")
                poetry(ctx, "install", verbose=verbose)
        else:
            poetry(ctx, "install", verbose=verbose)

    @task
    def devinstall(ctx, verbose: bool = False):
        """
        Install the package in develop mode and its dependencies.

        Args:
            verbose: Whether to run in verbose mode.
        """
        _make_conda_env_if_needed()

        with mark_as_develop_mode(all_packages=True):
            poetry(ctx, "lock --no-update")
            poetry(ctx, "install", verbose=verbose)

    @contextmanager
    def mark_as_develop_mode(
        projects: Optional[List[str]] = None, all_packages: bool = False
    ):
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
                        if not key.startswith("robocorp-"):
                            continue

                        # Changes something as:
                        # robocorp-log = "0.1.0"
                        # to:
                        # robocorp-log = {path = "../log/", develop = true
                        name = key[len("robocorp-") :]
                        if all_packages or (projects and name in projects):
                            dependencies[key] = dict(path=f"../{name}/", develop=True)
            yield
        finally:
            for roundtrip in roundtrips:
                roundtrip.restore()

    def _collect_docs_to_lint() -> List[Union[str, Path]]:
        # Collects Markdown documents paths to be passed to the Markdown lint tool.
        # FIXME(cmin764; 3 Apr 2024): Improve this into a dynamic path list by keeping
        #  only the *.md files not containing the linting-ignore HTML comment tag as
        #  observed with the generated API ones.
        docs_path = Path("docs")
        static_paths = [
            "README.md",
            docs_path / "guides",
            docs_path / "CHANGELOG.md",
        ]
        # Required since the Markdown lint tool doesn't currently have a way to
        #  configure directories/files to exclude.
        # See GH Issue: https://github.com/markdownlint/markdownlint/issues/368
        return static_paths

    @task
    def lint(ctx, strict: bool = False):
        """Run static analysis and formatting checks.

        Currently, it runs the following in this order:
            - Ruff basic checks, then the formatting ones
            - isort for sorting the imports
            - Optionally Pylint if enabled through the `strict` switch
            - Markdown lint if available in the system

        Args:
            strict: Whether to enable the more strict Pylint as well.
        """
        poetry(ctx, f"run ruff {TARGETS}")
        poetry(ctx, f"run ruff format --check {RUFF_ARGS} {TARGETS}")
        poetry(ctx, f"run isort --check {TARGETS}")
        if strict:
            poetry(ctx, f"run pylint --rcfile {ROOT / '.pylintrc'} src")

        # NOTE(cmin764): Markdown lint can be installed as a gem with Ruby.
        #  Instructions on GitHub page: https://github.com/markdownlint/markdownlint
        resolved_path = shutil.which("mdl")
        if resolved_path:
            print("Running Markdown lint over the hand-written docs...")
            docs_paths = " ".join(map(str, _collect_docs_to_lint()))
            cmd = f"{resolved_path} --config {ROOT / '.mdlrc'} {docs_paths}"
            subprocess.check_call(shlex.split(cmd))
        else:
            print(
                "Markdown lint wasn't found in PATH, consider installing and adding it"
                " in order to be able to lint package's *.md documents."
            )

    @task
    def typecheck(ctx, strict: bool = False):
        """Type check code"""
        cmd = [
            ctx,
            "run mypy",
            "--follow-imports=silent",
            "--show-column-numbers",
            "--namespace-packages",
            "--explicit-package-bases",
        ]
        cmd.extend(source_directories)
        if strict:
            cmd.append("--strict")
        poetry(*cmd)

    @task
    def pretty(ctx):
        """Auto-format code and sort imports"""
        poetry(ctx, f"run ruff --fix {TARGETS}")
        poetry(ctx, f"run ruff format {RUFF_ARGS} {TARGETS}")
        poetry(ctx, f"run isort {TARGETS}")

    @task
    def test(ctx, test: Optional[str] = None):
        """Run unittests"""
        cmd = "run pytest -rfE -vv"

        if test:
            cmd += f" {test}"

        if parallel_tests:
            cmd += " -n auto"

        poetry(ctx, cmd)

    @task
    def doctest(ctx):
        """Statically verify documentation examples."""
        pattern = re.compile(r"^\s*```python([\s\S]*?)\s*```", re.MULTILINE)
        files = [
            (root / "src").rglob("*.py"),
            (root / "docs" / "guides").rglob("*.md"),
        ]

        output = ""
        for path in chain(*files):
            dirname = to_identifier(path.parent.name)
            filename = to_identifier(path.name)

            content = path.read_text()
            matches = re.findall(pattern, content)
            if not matches:
                continue

            print(f"Found examples in: {path}")
            output += f"\n# {path.name}\n"
            for index, match in enumerate(matches):
                code = textwrap.indent(textwrap.dedent(match), "    ")
                output += f"\ndef codeblock_{dirname}_{filename}_{index}() -> None:"
                output += code
                output += "\n"

        if not output:
            print("No example blocks found")
            return

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            print(f"Validating project: {root.name}")
            for lineno, line in enumerate(output.splitlines(), 1):
                print(f"{lineno:3}: {line}")

            tmp.write(output)
            tmp.close()  # Fix for Windows
            poetry(ctx, f"run mypy --strict {tmp.name}")

    @task
    def build(ctx):
        """Build distributable .tar.gz and .wheel files"""
        poetry(ctx, "build")

    @task
    def publish(ctx, token: str):
        """Publish to PyPI"""
        poetry(ctx, f"config pypi-token.pypi {token}")
        poetry(ctx, "publish")

    @task
    def docs(ctx, check: bool = False, validate: bool = False):
        """Build API documentation"""
        if validate:
            poetry(ctx, "run lazydocs", "--validate", package_name)
            return

        output_path = root / "docs" / "api"
        if not output_path.exists():
            print("Docs output path does not exist. Skipping...")
            return

        for path in output_path.iterdir():
            path.unlink()

        poetry(
            ctx,
            "run lazydocs",
            "--no-watermark",
            "--remove-package-prefix",
            f"--src-base-url {REPOSITORY_URL}",
            "--overview-file README.md",
            f"--output-path {output_path}",
            package_name,
        )

        if check:
            if check_document_changes(ctx):
                output = run(ctx, "git --no-pager diff -- docs/api")
                raise RuntimeError(
                    f"There are uncommitted docs changes. Changes: {output.stdout}"
                )

    def check_document_changes(ctx):
        """
        Check if there were new document changes generated by lazydocs and
        are uncommited.

        Returns:
            True if there are new changes, False otherwise.
        """
        changed_files = (
            run(ctx, "git --no-pager diff --name-only -- docs/api", hide=True)
            .stdout.strip()
            .splitlines()
        )

        return bool(changed_files)

    @task(lint, typecheck, test)
    def check_all(ctx):
        """Run all checks"""
        ctx.run("inv docs --check")

    def _get_module_version(ctx) -> str:
        command = f'"import {package_name}; print({package_name}.__version__)"'
        return poetry(ctx, f"run python -c {command}").stdout.strip()

    @task
    def make_release(ctx):
        """Create a release tag"""
        import semver

        result = run(ctx, "git rev-parse --abbrev-ref HEAD", hide=True)
        branch = result.stdout.strip()
        if branch != "master":
            sys.stderr.write(f"Not on master branch: {branch}\n")
            sys.exit(1)

        current_version = _get_module_version(ctx)
        previous_tag = get_tag(tag_prefix)
        previous_version = previous_tag.split("-")[-1]

        if not previous_version:
            print(f"No previous release for {package_name}")
        elif semver.compare(current_version, previous_version) <= 0:
            sys.stderr.write(
                f"Current version older/same than previous:"
                f" {current_version} <= {previous_version}\n"
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

        print(f"Pushing tag: {current_tag}")
        run(ctx, f"git push origin {current_tag}")

    @task
    def check_tag_version(ctx):
        """
        Checks if the current tag matches the latest version (exits with 1 if it
        does not match and with 0 if it does match).
        """
        module_version = _get_module_version(ctx)
        tag = get_tag(tag_prefix)
        version = tag[tag.rfind("-") + 1 :]

        if module_version == version:
            sys.stderr.write(f"Version matches ({version}) (exit(0))\n")
            sys.exit(0)
        else:
            sys.stderr.write(
                f"Version does not match ({tag_prefix}: {module_version} !="
                f" repo tag: {version}).\nTags:{get_all_tags(tag_prefix)}\n(exit(1))\n"
            )
            sys.exit(1)

    def update_changelog_file(file: Path, version: str):
        """Update the changelog file with the new version and changes"""

        if not file.exists():  # usually happening with the meta one
            print("No CHANGELOG file found, skipping update.")
            return

        with open(file, "r+") as stream:
            content = stream.read()

            new_version = f"## {version} - {datetime.today().strftime('%Y-%m-%d')}"
            changelog_start = re.search(r"# Changelog", content).end()
            if not changelog_start:
                print(
                    f"Did not find # Changelog in the changelog:\n{file}\n"
                    f"Please update Changelog before proceeding."
                )
                sys.exit(1)

            unreleased_match = re.search(r"## Unreleased", content, flags=re.IGNORECASE)
            double_newline = "\n\n"

            new_content = content[:changelog_start] + double_newline + "## Unreleased"
            if unreleased_match:
                released_content = content.replace(
                    unreleased_match.group(), new_version
                )
                new_content += released_content[changelog_start:]
            else:
                new_content += double_newline + new_version + content[changelog_start:]

            stream.seek(0)
            stream.write(new_content)
            print("Changed: ", file)

            if not unreleased_match:
                print(
                    f"\nDid not find ## Unreleased in the changelog:\n{file}\n"
                    f"Please update Changelog before proceeding.\n"
                    f"It was updated to have the proper sessions already..."
                )
            sys.exit(1)

    @task
    def set_version(ctx, version):
        """Sets a new version for the project in all the needed files"""
        valid_version_pattern = re.compile(r"^\d+\.\d+\.\d+$")
        if not valid_version_pattern.match(version):
            print(
                f"Invalid version: {version}. Must be in the format major.minor.hotfix"
            )
            return

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
        update_changelog_file(Path(root, "docs", "CHANGELOG.md"), version)

    return locals()
