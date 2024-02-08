from importlib.machinery import SourceFileLoader
from pathlib import Path


TASKS_PATH = Path(__file__).resolve()


# Since the `robocorp-devutils` dependency is available in the local Poetry isolated
#  environment only, we won't have it available with Invoke commands running outside
#  such environment.
def load_devutils():
    devutils_path = (
        TASKS_PATH.parent.parent /
        "devutils" / "src" / "devutils" / "__init__.py"
    )
    assert devutils_path.is_file(), f"{devutils_path} does not exist"
    return SourceFileLoader("devutils", str(devutils_path)).load_module()

# But we still need to import the package in order to expose the common Invoke tasks.
try:
    import devutils
except ImportError:
    devutils = load_devutils()

common_tasks = devutils.build_common_tasks(TASKS_PATH.parent, "robocorp.excel")
globals().update(common_tasks)
