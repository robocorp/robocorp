import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml

from . import pyproject


def generate(conda_path: str):
    curdir = os.getcwd()
    config = pyproject.load()

    # NB: conda.yaml path needs to be relative to robot.yaml
    conda_config = str(Path(conda_path).relative_to(curdir))

    # TODO: Create some global place where we define this,
    # probably next to the pyproject schema
    output_path = config.get("output", "output")

    # TODO: Parse tasks via inner framework
    content = {
        "tasks": {"Python Run": {"shell": "python tasks.py"}},
        "condaConfigFile": conda_config,
        "artifactsDir": output_path,
        "ignoreFiles": [".gitignore"],
        "PATH": ["."],
        "PYTHONPATH": ["."],
    }

    tempfile = NamedTemporaryFile(
        delete=False,
        dir=curdir,
        suffix=".yaml",
        prefix=".robot_",
    )

    with open(tempfile.name, "w") as file:
        yaml.dump(content, file, sort_keys=False)

    return tempfile.name
