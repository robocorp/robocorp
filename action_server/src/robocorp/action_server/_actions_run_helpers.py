import os
import typing
from pathlib import Path
from typing import Dict

if typing.TYPE_CHECKING:
    from robocorp.action_server._models import Action, ActionPackage
    from robocorp.action_server._settings import Settings


def _add_preload_actions_dir_to_env_pythonpath(env: Dict[str, str]) -> None:
    from robocorp.action_server import _preload_actions

    p = Path(_preload_actions.__file__)
    if "__init__" in p.name:
        p = p.parent
    curr_pythonpath = env.get("PYTHONPATH", "")
    if not curr_pythonpath:
        env["PYTHONPATH"] = str(p)
    else:
        env["PYTHONPATH"] = f"{p}{os.pathsep}{curr_pythonpath}"


def get_action_package_cwd(
    settings: "Settings", action_package: "ActionPackage"
) -> Path:
    directory = Path(action_package.directory)

    # Make it absolute now!
    if not directory.is_absolute():
        directory = (settings.datadir / directory).absolute()

    if not directory.exists():
        raise RuntimeError(
            f"""Error. Unable to run because action package directory:
{directory} 
does not exist.
This usually happens because the action was moved to a different
location. To fix please move it back to the original location or
import it again from the new location.
"""
        )
    return directory
