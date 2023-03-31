import hashlib
import json
from pathlib import Path

from robo_cli import rcc
from robo_cli.config.context import generate_configs
from robo_cli.paths import ROOT, home_path

Variables = dict[str, str]

ENV_CACHE = home_path() / ".envcache.json"


def ensure() -> Variables:
    with generate_configs() as (conda_path, _):
        digest = _calculate_hash(ROOT, conda_path)
        cache = _load_cache()

        if cached := cache.get(digest):
            return cached

        variables = _create_environment(conda_path, digest)
        cache[digest] = variables
        _save_cache(cache)

        return variables


def _load_cache() -> dict[str, Variables]:
    try:
        with open(ENV_CACHE, "r", encoding="utf-8") as fd:
            return json.load(fd)
    except FileNotFoundError:
        return {}


def _save_cache(cache: dict[str, Variables]):
    ENV_CACHE.parent.mkdir(parents=True, exist_ok=True)
    with open(ENV_CACHE, "w", encoding="utf-8") as fd:
        json.dump(cache, fd)


def _create_environment(conda_path: Path, digest: str) -> Variables:
    space = f"robo-{digest}"
    variables = rcc.holotree_variables(conda_path, space)
    return variables


def _calculate_hash(project_path: Path, conda_path: Path) -> str:
    md5 = hashlib.md5()
    md5.update(str(project_path).encode("utf-8"))

    with open(conda_path, "rb") as fd:
        while chunk := fd.read(8192):
            md5.update(chunk)

    return md5.hexdigest()[:16]
