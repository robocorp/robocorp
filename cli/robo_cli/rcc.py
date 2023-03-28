import json
import os
from pathlib import Path

from robo_cli.config import generate_rcc
from robo_cli.config.pyproject import DEFAULT_PYPROJECT
from robo_cli.process import Process

# Convert to absolute path when vendored to not require PATH to be correct
RCC_EXECUTABLE = "rcc"


def _execute(*args):
    cmd = [RCC_EXECUTABLE] + [str(arg).strip() for arg in args]

    proc = Process(args=cmd)
    proc.on_stdout(lambda line: print(line))
    proc.on_stderr(lambda line: print(line))

    stdout, _ = proc.run()
    return "\n".join(stdout)


def run():
    with generate_rcc() as (_, robot_config):
        _execute("run", "--robot", robot_config)


def deploy(workspace_id, robot_id):
    with generate_rcc() as (conda_config, robot_config):
        # TODO: Copy tempfiles into temporary "deploy" folder with all of the code?
        # TODO: We need to generate -r robot id and -w workspace or get them from
        # pyproject.toml
        _execute("cloud", "push", "-w", workspace_id, "-r", robot_id)


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
