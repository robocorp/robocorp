import os
import tomllib
import yaml

DEFAULT_PYPROJECT = """
[tool.robo]
name = "Simple Automation"
description = "Very simple automation "
readme = "README.md"

[tool.robo.dependencies]
rpaframework="22.0.0"
"""


def read_toml():
    with open("pyproject.toml", "rb") as f:
        return tomllib.load(f)


def generate_yamls():
    parsed = read_toml()
    raw_deps: dict[str, str] = parsed["tool"]["robo"]["dependencies"]
    # TODO: check that this can handle ^ and such? or do we support those at all
    deps_as_list = [f"{k}=={v}" for k, v in raw_deps.items()]

    conda_yaml = {
        "channels": ["conda-forge"],
        "dependencies": [
            "python=3.9.13",
            "pip=22.1.2",
            {
                "pip": deps_as_list,
            },
        ],
    }

    with open("conda.yaml", "w") as f:
        yaml.dump(conda_yaml, f, sort_keys=False)

    robot_yaml = {
        "tasks": {"Python Run": {"shell": "python tasks.py"}},
        "condaConfigFile": "conda.yaml",
        "artifactsDir": "output",
        "ignoreFiles": [".gitignore"],
        "PATH": ["."],
        "PYTHONPATH": ["."],
    }

    with open("robot.yaml", "w") as f:
        yaml.dump(robot_yaml, f, sort_keys=False)


def delete_yamls():
    os.remove("conda.yaml")
    os.remove("robot.yaml")
