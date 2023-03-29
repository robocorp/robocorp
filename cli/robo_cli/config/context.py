import os
from contextlib import contextmanager
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

from . import conda, robot


@contextmanager
def generate_rcc():
    conda_config = None
    robot_config = None

    try:
        conda_config = conda.generate()
        robot_config = robot.generate(conda_config)
        yield conda_config, robot_config
    finally:
        if conda_config is not None:
            os.unlink(conda_config)
        if robot_config is not None:
            os.unlink(robot_config)


@contextmanager
def temp_robot_folder():
    try:
        with generate_rcc() as (conda_config, robot_config):
            dir = TemporaryDirectory()
            shutil.copy(conda_config, Path(dir.name) / "conda.yaml")
            shutil.copy(robot_config, Path(dir.name) / "robot.yaml")
            shutil.copy(".gitignore", Path(dir.name) / ".gitignore")
            # TODO: support some kind of discovery for what python files to copy
            shutil.copy("tasks.py", Path(dir.name) / "tasks.py")
            shutil.copy("pyproject.toml", Path(dir.name) / "pyproject.toml")
            yield dir
    finally:
        dir.cleanup()
