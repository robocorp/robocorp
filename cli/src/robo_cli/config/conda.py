from pathlib import Path
from tempfile import NamedTemporaryFile
from typing_extensions import Literal

import yaml

from robo_cli import paths

from . import pyproject


def generate(env: Literal["dependencies", "dev-dependencies"]) -> Path:
    config = pyproject.load()

    # TODO: Create some global place where we define this,
    # probably next to the pyproject schema
    python_version = config.get("python", "3.9.13")
    pip_version = "22.1.2"

    dependencies = config.get(env, {})
    pip_deps = _to_pip_deps(dependencies)

    content = {
        "channels": ["conda-forge"],
        "dependencies": [
            f"python={python_version}",
            f"pip={pip_version}",
            {
                "pip": pip_deps,
            },
        ],
    }

    tempfile = NamedTemporaryFile(
        delete=False,
        dir=paths.ROOT,
        suffix=".yaml",
        prefix=".conda_",
    )

    with open(tempfile.name, "w") as file:
        yaml.dump(content, file, sort_keys=False)

    return Path(tempfile.name)


def _to_pip_deps(robo_deps):
    pip_deps = []
    for key, value in robo_deps.items():
        key = str(key)
        value = str(value)
        if _is_file_path(value):
            pip_deps.append(value)
        else:
            pip_deps.append(f"{key}=={value}")
    return pip_deps


def _is_file_path(name: str):
    try:
        return (paths.ROOT / name).is_file() or Path(name).absolute().is_file()
    except OSError:
        return False
