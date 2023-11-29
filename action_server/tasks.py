import os
import platform
import shutil
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

# Add the devutils even if the poetry env isn't setup (to do a 'inv devinstall').
try:
    import devutils
except ImportError:
    devutils_src = Path(__file__).absolute().parent.parent / "devutils" / "src"
    assert devutils_src.exists(), f"{devutils_src} does not exist."
    sys.path.append(str(devutils_src))

from devutils.invoke_utils import build_common_tasks
from invoke import Context, task

CURDIR = Path(__file__).parent.absolute()


globals().update(
    build_common_tasks(Path(__file__).absolute().parent, "robocorp.action_server")
)


@contextmanager
def chdir(path: Path):
    old = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(old)


def run(ctx: Context, *args: str, **options):
    cmd = " ".join(args)
    options.setdefault("pty", sys.platform != "win32")
    options.setdefault("echo", True)
    ctx.run(cmd, **options)


@task
def build_frontend(ctx: Context, debug: bool = False, install: bool = True):
    """Build static .html frontend"""
    with chdir(CURDIR / "frontend"):
        if install:
            run(ctx, "npm", "ci", "--no-audit", "--no-fund")
        if debug:
            run(ctx, "npm", "run", "build:debug")
        else:
            run(ctx, "npm", "run", "build")

    index_src = CURDIR / "frontend" / "dist" / "index.html"
    index_dst = CURDIR / "src" / "robocorp" / "action_server" / "_static" / "index.html"

    index_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(index_src, index_dst)


@task
def download_rcc(ctx: Context, system: Optional[str] = None) -> None:
    """
    Downloads RCC in the place where the action server expects it
    """
    run(ctx, "python -m robocorp.action_server download-rcc")
