import urllib.request
import os
import platform
import stat
import sys
from pathlib import Path

from invoke import task

CURDIR = Path(__file__).parent
SRC = CURDIR / "src"

RCC_URL = {
    "Windows": "https://downloads.robocorp.com/rcc/releases/v11.28.0/windows64/rcc.exe",
    "Darwin": "https://downloads.robocorp.com/rcc/releases/v11.28.0/macos64/rcc",
    "Linux": "https://downloads.robocorp.com/rcc/releases/v11.28.0/linux64/rcc",
}[platform.system()]


def poetry(ctx, *parts):
    args = " ".join(str(part) for part in parts)
    ctx.run(f"poetry {args}", pty=sys.platform != "win32", echo=True)


@task
def install(ctx):
    poetry(ctx, "install")

    # Download RCC
    filename = "rcc.exe" if platform.system() == "Windows" else "rcc"
    path = CURDIR / "resources" / "bin" / filename
    path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Downloading '{RCC_URL}' to '{path}'")
    urllib.request.urlretrieve(RCC_URL, path)

    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


@task
def lint(ctx):
    """Run static analysis and formatting checks"""
    poetry(ctx, f"run ruff {SRC}")
    poetry(ctx, f"run black --check {SRC}")
    poetry(ctx, f"run isort --check {SRC}")


@task
def typecheck(ctx):
    poetry(ctx, f"run mypy {SRC}")


@task
def test(ctx):
    """Run unittests"""
    poetry(ctx, "run pytest")


@task(lint, typecheck, test)
def check_all(ctx):
    """Run all checks"""
    pass


@task
def pretty(ctx):
    """Automatically format code"""
    poetry(ctx, f"run black {SRC} {CURDIR / 'tests'}")
    poetry(ctx, f"run isort {SRC} {CURDIR / 'tests'}")


@task
def build(ctx):
    """Build executable"""
    poetry(ctx, f"run pyinstaller {CURDIR / 'pyinstaller.spec'}")
