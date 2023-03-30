import tomllib
from functools import lru_cache
from typing import NotRequired, TypedDict

from .validator import validate_schema

TOOL_ROBO = TypedDict(
    "TOOL_ROBO",
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
            if validate_schema(section, TOOL_ROBO):
                return section
            raise RuntimeError  # Unreachable code
        except (KeyError, ValueError) as err:
            raise ValueError(f"Invalid configuration in pyproject.toml: {err}") from err
