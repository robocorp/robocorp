import tomllib
from typing import TypedDict, NotRequired
from functools import lru_cache
from .validator import validate_schema

ROBO_SECTION = TypedDict(
    "Schema",
    {
        "name": str,
        "description": NotRequired[str],
        "python": NotRequired[str],
        "dependencies": NotRequired[dict[str, str]],
        "dev-dependencies": NotRequired[dict[str, str]],
    },
)


# TODO: Should an absolute path come from some global context/config?
@lru_cache
def load(path="pyproject.toml"):
    with open(path, "rb") as file:
        try:
            content = tomllib.load(file)
            section = content["tool"]["robo"]
        except KeyError as err:
            raise ValueError("Missing tool.robo section in pyproject.toml") from err

        try:
            if validate_schema(section, ROBO_SECTION):
                return section
            raise RuntimeError  # Unreachable code
        except (KeyError, ValueError) as err:
            raise ValueError(f"Invalid configuration in pyproject.toml: {err}") from err
