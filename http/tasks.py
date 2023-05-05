import platform
from pathlib import Path
from invoke import task

CURDIR = Path(__file__).parent
SRC = CURDIR / "src"


def poetry(ctx, *parts):
    args = " ".join(str(part) for part in parts)
    ctx.run(f"poetry {args}", pty=platform.system() != "Windows", echo=True)


@task
def install(ctx):
    """Install dependencies"""
    poetry(ctx, "install")


@task
def lint(ctx):
    """Run static analysis and formatting checks"""
    poetry(ctx, f"run ruff {SRC}")
    poetry(ctx, f"run black --check {SRC}")
    poetry(ctx, f"run isort --check {SRC}")


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
        "robocorp.http",
    )
