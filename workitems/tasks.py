import os
from pathlib import Path

from devutils.invoke_utils import build_common_tasks

# Enable debug logging for tests
os.environ["RC_DEBUG_API"] = "1"

globals().update(
    build_common_tasks(Path(__file__).absolute().parent, "robocorp.workitems")
)
