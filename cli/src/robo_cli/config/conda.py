import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

import yaml

from robo_cli import paths

from . import pyproject

LOGGER = logging.getLogger(__name__)


def generate(develop=True) -> Path:
    config = pyproject.load()

    # TODO: Create some global place where we define this,
    # probably next to the pyproject schema
    python_version = config.get("python", "3.9.13")
    pip_version = "22.1.2"

    pip_deps = _generate_pip_deps(develop)

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


def _generate_pip_deps(develop: bool) -> list[str]:
    config = pyproject.load()

    dependencies = config.get("dependencies", {})
    if develop:
        dev_dependencies = config.get("dev-dependencies", {})
        if duplicates := (dependencies.keys() & dev_dependencies.keys()):
            names = ", ".join(duplicates)
            raise ValueError(
                f"Duplicate entries 'dependencies' and 'dev-dependencies': {names}"
            )
        dependencies.update(dev_dependencies)

    LOGGER.debug(dependencies)
    return _to_pip_deps(dependencies)


def _to_pip_deps(dependencies: dict[str, str]) -> list[str]:
    rows = []
    for key, value in dependencies.items():
        key = str(key)
        value = str(value)
        if _is_file_path(value):
            rows.append(value)
        else:
            rows.append(f"{key}=={value}")
    return rows


def _is_file_path(name: str) -> bool:
    try:
        return (paths.ROOT / name).is_file() or Path(name).absolute().is_file()
    except OSError:
        return False
