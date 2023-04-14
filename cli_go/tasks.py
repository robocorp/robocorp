import urllib.request
import os
import platform
import stat
from pathlib import Path

from invoke import task

CURDIR = Path(__file__).parent
BUILD = CURDIR / "build"

RCC_VERSION = "11.28.0"
RCC_URL = {
    "Windows": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/windows64/rcc.exe",
    "Darwin": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/macos64/rcc",
    "Linux": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/linux64/rcc",
}[platform.system()]


def run(ctx, *parts):
    args = " ".join(str(part) for part in parts)
    ctx.run(args, pty=platform.system() != "Windows", echo=True)


@task
def pretty(ctx):
    """Auto-format code"""
    run(ctx, "gofmt", "-s", "-w", CURDIR)


@task
def build(ctx):
    """Build robo binary"""
    BUILD.mkdir(parents=True, exist_ok=True)
    run(ctx, "go", "build", "-o", BUILD / "robo", CURDIR)


@task
def include(ctx):
    """Download static assets to include/ directory"""
    filename = "rcc.exe" if platform.system() == "Windows" else "rcc"
    path = CURDIR / "include" / "bin" / filename

    print(f"Downloading '{RCC_URL}' to '{path}'")
    urllib.request.urlretrieve(RCC_URL, path)

    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
