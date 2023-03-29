import tomllib
from functools import lru_cache


# TODO: Should an absolute path come from some global context/config?
# TODO: Create a schema/type for our config section
@lru_cache
def load(path="pyproject.toml"):
    with open(path, "rb") as file:
        try:
            content = tomllib.load(file)
            return content["tool"]["robo"]
        except KeyError:
            raise RuntimeError("Missing tool.robo section in pyproject.toml")
