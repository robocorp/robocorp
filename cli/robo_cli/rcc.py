import os
import platform
import subprocess
from pathlib import Path

from robo_cli.config import DEFAULT_PYPROJECT, generate_yamls, delete_yamls


def rcc_command(command: str, cwd=None, stdout=None):
    system = platform.system()
    if system == "Windows":
        command.replace("rcc", "rcc.exe")

    command_and_args = command.split(" ")
    return subprocess.run(
        command_and_args, shell=False, cwd=cwd, check=True, stdout=stdout
    )


def run():
    try:
        generate_yamls()
        rcc_command("rcc run")
    finally:
        delete_yamls()


def deploy():
    try:
        generate_yamls()
        # TODO we need to generate -r robot id and -w workspace or get them from
        # pyproject.toml
        rcc_command("rcc cloud push")
    finally:
        delete_yamls()


def new_project(name: str):
    os.mkdir(name)
    new_folder = Path(name)
    with open(new_folder / "pyproject.toml", "w") as f:
        f.write(DEFAULT_PYPROJECT)

    with open(new_folder / "tasks.py", "w") as f:
        f.write("from robo import task\n\n")
        f.write("def task():\n")
        f.write(f'    print("Hello")\n')
