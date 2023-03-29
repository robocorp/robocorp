import json
import shutil
from pathlib import Path

from robo_cli.config import generate_configs, generate_robot
from robo_cli.process import Process, ProcessError

# Convert to absolute path when vendored to not require PATH to be correct
RCC_EXECUTABLE = "rcc"


def _execute(*args):
    cmd = [RCC_EXECUTABLE] + [str(arg).strip() for arg in args]

    proc = Process(args=cmd)
    # proc.on_stdout(lambda line: print(line))
    # proc.on_stderr(lambda line: print(line))

    try:
        stdout, _ = proc.run()
    except ProcessError as exc:
        # If there was an exception we want to avoid the huge CLI traceback and print
        # the subprocess errors
        print(("\n").join(exc.stdout))
        print(("\n").join(exc.stderr))
        exit(1)

    return "\n".join(stdout)


def run():
    with generate_configs() as (_, robot_config):
        _execute("run", "--robot", robot_config)


def deploy(workspace_id, robot_id):
    with generate_robot() as root:
        _execute(
            "cloud",
            "push",
            "--directory",
            root.name,
            "-w",
            workspace_id,
            "-r",
            robot_id,
        )


def export() -> Path:
    with generate_robot() as root:
        _execute("robot", "wrap", "--directory", root.name)
        dist = Path("dist")
        dist.mkdir(parents=True, exist_ok=True)
        dst = dist / "robot.zip"
        shutil.move("robot.zip", str(dst))
        return dst


def list_workspaces() -> dict[str, dict[str, str]]:
    stdout = _execute("cloud", "workspace", "--json")
    raw_workspaces: list[dict] = json.loads(stdout)
    workspaces = {
        ws["name"]: {"id": ws["id"], "url": ws["url"]} for ws in raw_workspaces
    }
    return workspaces
