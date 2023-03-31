import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from . import conda, robot


@contextmanager
def generate_configs(
    deps_type: Literal["dependencies", "dev-dependencies"] = "dependencies"
):
    conda_config = None
    robot_config = None

    try:
        conda_config = conda.generate(deps_type)
        robot_config = robot.generate(conda_config)
        yield conda_config, robot_config
    finally:
        if conda_config is not None:
            os.unlink(conda_config)
        if robot_config is not None:
            os.unlink(robot_config)


@contextmanager
def generate_robot():
    with TemporaryDirectory() as root:
        with generate_configs() as (conda_config, robot_config):
            root = Path(root)
            shutil.copy(conda_config, root / "conda.yaml")
            shutil.copy(robot_config, root / "robot.yaml")
            shutil.copy(".gitignore", root / ".gitignore")
            # TODO: support some kind of discovery for what python files to copy
            shutil.copy("tasks.py", root / "tasks.py")
            shutil.copy("pyproject.toml", root / "pyproject.toml")
            yield root
