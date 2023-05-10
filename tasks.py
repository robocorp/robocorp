from invoke import task
from pathlib import Path
import invoke
import subprocess

CURDIR: Path = Path(__file__).absolute().parent


def iter_project_dirs():
    for d in CURDIR.iterdir():
        if d.is_dir():
            if (d / "pyproject.toml").exists():
                yield d


@task
def update_poetry_lock(ctx: invoke.Context) -> None:
    """Runs 'poetry lock' on all projects with a pyproject.toml."""
    for project_dir in iter_project_dirs():
        # Note: can't use threads to speed it up. poetry (or pip) just fail...
        subprocess.check_call(["poetry", "lock"], cwd=project_dir)


@task
def update_pyproject_dev_deps(ctx) -> None:
    """
    Updates the development dependencies on all pyproject.toml files to the one below.

    It'd be nice if we could do it in a single file and reference it, but this
    is a poetry shortcoming that'll never be fixed:

    https://github.com/python-poetry/poetry/issues/1055

    So, we have to manually do it (and this command line helps us making it
    consistently to all pyproject.toml files).

    """

    import re

    pattern = re.compile(
        r"\[tool\.poetry\.group\.dev\.dependencies\].*?(?=\[)", re.DOTALL
    )

    for project_dir in iter_project_dirs():
        pyproject = project_dir / "pyproject.toml"
        additional = """robocorp-devutils = {path = "../devutils/", develop = true}
"""

        if project_dir.name == "devutils":
            additional = ""

        if project_dir.name == "workitems":
            additional = """types-requests = "^2.30.0.0"
types-pyyaml = "^6.0.12.9"
robocorp-devutils = {path = "../devutils/", develop = true}
"""
        new_content = """[tool.poetry.group.dev.dependencies]
black = "^23.1.0"
ruff = "^0.0.255"
mypy = "^1.1.1"
pytest = "^7.2.2"
pytest-xdist = "^3.2.1"
pytest-regressions = "1.0.6"
pydocstyle = "^6.3.0"
isort = "^5.12.0"
types-invoke = "^2.0"
invoke = "^2.0"
lazydocs = { git = "https://github.com/robocorp/lazydocs.git" }
%s
""" % (
            additional,
        )

        print("Updating", pyproject.absolute())
        contents = pyproject.read_bytes().decode("utf-8")
        pyproject.write_bytes(pattern.sub(new_content, contents).encode("utf-8"))
