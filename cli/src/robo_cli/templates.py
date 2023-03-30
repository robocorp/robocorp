import shutil
from pathlib import Path

from robo_cli.paths import resources_path

TEMPLATE_PATH = resources_path() / "templates"


def list_templates():
    return [path.name for path in TEMPLATE_PATH.iterdir() if path.is_dir()]


def copy_template(dst: Path, template: str) -> Path:
    # TODO: Validate names nicer
    shutil.copytree(TEMPLATE_PATH / template, dst)
    return dst
