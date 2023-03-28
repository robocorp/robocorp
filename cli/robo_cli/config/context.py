import os
from contextlib import contextmanager

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
