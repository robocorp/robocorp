from pathlib import Path
from devutils.invoke_utils import build_common_tasks


globals().update(build_common_tasks(Path(__file__).absolute().parent, "robocorp.http"))
