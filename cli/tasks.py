from pathlib import Path

from invoke import task

CURDIR = Path(__file__).parent
SRC = CURDIR / "src" / "robo_cli"


def poetry(ctx, *parts):
    args = " ".join(str(part) for part in parts)
    ctx.run(f"poetry run {args}", pty=True, echo=True)


@task
def lint(ctx):
    """Run static analysis and formatting checks"""
    poetry(ctx, f"ruff {SRC}")
    poetry(ctx, f"black --check {SRC}")
    poetry(ctx, f"isort --check {SRC}")


@task
def test(ctx):
    """Run unittests"""
    poetry(ctx, "pytest")


@task
def pretty(ctx):
    """Automatically format code"""
    poetry(ctx, f"black {SRC} {CURDIR / 'tests'}")
    poetry(ctx, f"isort {SRC} {CURDIR / 'tests'}")


@task
def build(ctx):
    """Build executable"""
    poetry(ctx, f"pyinstaller {CURDIR / 'pyinstaller.spec'}")
