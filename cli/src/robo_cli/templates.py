import shutil
from pathlib import Path

from robo_cli.resources import resource_path

TEMPLATE_PATH = resource_path("templates")


def list_templates():
    return [path.name for path in TEMPLATE_PATH.iterdir() if path.is_dir()]


def copy_template(dst: Path, template: str):
    # TODO: Validate names nicer
    shutil.copytree(TEMPLATE_PATH / template, dst)
