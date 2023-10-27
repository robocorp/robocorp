import os
import platform
import shutil
from contextlib import contextmanager
from pathlib import Path

from invoke import task, Context

from devutils.invoke_utils import build_common_tasks

CURDIR = Path(__file__).parent


globals().update(build_common_tasks(Path(__file__).absolute().parent, "robocorp.task_server"))


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
    options.setdefault("pty", platform.system() == "Windows")
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
    index_dst = CURDIR / "src" / "robocorp" / "task_server" / "_static" / "index.html"

    index_dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(index_src, index_dst)
