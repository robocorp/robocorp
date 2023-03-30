import json
import platform
import shutil
from pathlib import Path
from typing import Optional

from robo_cli.config import generate_robot
from robo_cli.paths import resources_path
from robo_cli.process import Listener, Process


def _resolve_rcc_path():
    exe = "rcc.exe" if platform.system() == "Windows" else "rcc"
    return resources_path() / "bin" / exe


RCC_PATH = _resolve_rcc_path()
RCC_CONTROLLER = "robo-cli"


def _execute(
    *args,
    on_stdout: Optional[Listener] = None,
    on_stderr: Optional[Listener] = None,
):
    cmd = [str(RCC_PATH)] + [str(arg).strip() for arg in args]

    proc = Process(args=cmd)
    if on_stdout:
        proc.on_stdout(on_stdout)
    if on_stderr:
        proc.on_stderr(on_stderr)

    stdout, stderr = proc.run()
    return stdout, stderr


def holotree_variables(conda_config: Path, space: str) -> dict[str, str]:
    stdout, _ = _execute(
        "holotree",
        "variables",
        "--json",
        "--colorless",
        "--space",
        space,
        "--controller",
        RCC_CONTROLLER,
        str(conda_config),
    )

    variables = dict((var["key"], var["value"]) for var in json.loads(stdout))
    return variables


def robot_wrap() -> Path:
    # TODO: Move this context to the callee
    with generate_robot() as root:
        _execute("robot", "wrap", "--directory", root.name)
        dist = Path("dist")
        dist.mkdir(parents=True, exist_ok=True)
        dst = dist / "robot.zip"
        shutil.move("robot.zip", str(dst))
        return dst


def cloud_workspace() -> dict[str, dict[str, str]]:
    stdout, _ = _execute("cloud", "workspace", "--json")
    raw_workspaces: list[dict] = json.loads(stdout)
    workspaces = {
        ws["name"]: {"id": ws["id"], "url": ws["url"]} for ws in raw_workspaces
    }
    return workspaces


def cloud_push(workspace_id, robot_id):
    # TODO: Move this context to the callee
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
