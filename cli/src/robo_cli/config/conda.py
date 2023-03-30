from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml

from robo_cli import paths

from . import pyproject


def _to_pip_deps(dependencies):
    # TODO: Parse different types (path, URL, semver ranges, etc.)
    return [f"{k}=={v}" for k, v in dependencies.items()]


def generate() -> Path:
    config = pyproject.load()

    # TODO: Create some global place where we define this,
    # probably next to the pyproject schema
    python_version = config.get("python", "3.9.13")
    pip_version = "22.1.2"

    dependencies = config.get("dependencies", {})
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
