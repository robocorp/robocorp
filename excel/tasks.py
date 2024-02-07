from importlib.machinery import SourceFileLoader
from pathlib import Path

# Since the `robocorp-devutils` dependency is available in the local Poetry isolated
#  environment only, we won't have it available with Invoke commands running outside
#  such environment.
tasks_path = Path(__file__).absolute()
invoke_utils_path = (
    tasks_path.parent.parent /
    "devutils" / "src" / "devutils" / "invoke_utils.py"
)
assert invoke_utils_path.is_file(), f"{invoke_utils_path} does not exist"

# But we still need to import the package in order to expose the common Invoke tasks.
try:
    from devutils import invoke_utils
except ImportError:
    invoke_utils = SourceFileLoader(
        "invoke_utils", str(invoke_utils_path)
    ).load_module()

common_tasks = invoke_utils.build_common_tasks(tasks_path.parent, "robocorp.excel")
globals().update(common_tasks)
