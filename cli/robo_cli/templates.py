import shutil
from pathlib import Path

# TODO: Use resource path for bundled project
TEMPLATE_PATH = Path(__file__).parent.parent / "templates"


def list_templates():
    return [path.name for path in TEMPLATE_PATH.iterdir() if path.is_dir()]


def copy_template(dst: Path, template: str):
    # TODO: Validate names nicer
    shutil.copytree(TEMPLATE_PATH / template, dst)
