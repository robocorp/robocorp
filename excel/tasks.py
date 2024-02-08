from importlib.machinery import SourceFileLoader
from pathlib import Path

# Since the `robocorp-devutils` dependency is available in the local Poetry isolated
#  environment only, we won't have it available with Invoke commands running outside
#  such environment.
tasks_path = Path(__file__).resolve()
devutils_path = (
    tasks_path.parent.parent /
    "devutils" / "src" / "devutils" / "__init__.py"
)
assert devutils_path.is_file(), f"{devutils_path} does not exist"

# But we still need to import the package in order to expose the common Invoke tasks.
try:
    import devutils
except ImportError:
    devutils = SourceFileLoader("devutils", str(devutils_path)).load_module()

common_tasks = devutils.build_common_tasks(tasks_path.parent, "robocorp.excel")
globals().update(common_tasks)
