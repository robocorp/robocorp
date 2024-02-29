import sys
from pathlib import Path

ROOT = Path(__file__).absolute().parent

# To run Invoke commands outside the Poetry env (like `inv install`), you'd need to
#  manually fiddle with Python's import path so the module we're interested into gets
#  available for import.
try:
    import devutils
except ImportError:
    devutils_src = ROOT.parent / "devutils" / "src"
    assert devutils_src.exists(), f"{devutils_src} does not exist!"
    sys.path.append(str(devutils_src))

from devutils.invoke_utils import build_common_tasks

common_tasks = build_common_tasks(ROOT, "robocorp.excel")
globals().update(common_tasks)
