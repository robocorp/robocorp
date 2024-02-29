import sys
from pathlib import Path

ROOT = Path(__file__).absolute().parent

try:
    import devutils
except ImportError:
    devutils_src = ROOT.parent / "devutils" / "src"
    assert devutils_src.exists(), f"{devutils_src} does not exist!"
    sys.path.append(str(devutils_src))

from devutils.invoke_utils import build_common_tasks

globals().update(build_common_tasks(ROOT, "robocorp.tasks"))
