import os
from pathlib import Path
import json

from robo_cli.config import DEFAULT_PYPROJECT, generate_yamls, delete_yamls
from robo_cli.process import Process

# Convert to absolute path when vendored to not require PATH to be correct
RCC_EXECUTABLE = "rcc"


def _execute(*args, listener=None):
    cmd = [RCC_EXECUTABLE] + [str(arg).strip() for arg in args]

    proc = Process(args=cmd)
    if listener:
        proc.add_listener(listener)

    stdout, _ = proc.run()
    return "\n".join(stdout)


def run():
    def _print_stderr(line: str):
        print(line)

    try:
        generate_yamls()
        _execute("run", listener=_print_stderr)
    finally:
        delete_yamls()


def deploy(workspace_id, robot_id):
    try:
        generate_yamls()
        # TODO we need to generate -r robot id and -w workspace or get them from
        # pyproject.toml
        _execute("cloud", "push", "-w", workspace_id, "-r", robot_id)
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
        f.write('    print("Hello")\n')

    with open(new_folder / ".gitignore", "w") as f:
        f.write("output/\n")


def get_workspaces() -> dict[str, dict[str, str]]:
    raw_output = _execute("cloud", "workspace", "--json")
    raw_workspaces: list[dict] = json.loads(raw_output)
    workspaces = {w["name"]: {"id": w["id"], "url": w["url"]} for w in raw_workspaces}
    return workspaces
