from pathlib import Path
import sys

# Add the devutils even if the poetry env isn't setup (to do a 'inv devinstall').
try:
    import devutils
except ImportError:
    devutils_src = Path(__file__).absolute().parent.parent / "devutils" / "src"
    assert devutils_src.exists(), f"{devutils_src} does not exist."
    sys.path.append(str(devutils_src))

from devutils.invoke_utils import build_common_tasks

globals().update(build_common_tasks(Path(__file__).absolute().parent, "robocorp.tasks"))
