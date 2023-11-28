import itertools
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from types import ModuleType
from typing import Callable, Dict, Iterator, List, Optional, Sequence

from robocorp.tasks._protocols import ITask


def module_name_from_path(path: Path, root: Path) -> str:
    """
    Return a dotted module name based on the given path, anchored on root.
    For example: path="projects/src/tests/test_foo.py" and root="/projects", the
    resulting module name will be "src.tests.test_foo".

    Based on: https://github.com/pytest-dev/pytest/blob/main/src/_pytest/pathlib.py
    """
    path = path.with_suffix("")
    try:
        relative_path = path.relative_to(root)
    except ValueError:
        # If we can't get a relative path to root, use the full path, except
        # for the first part ("d:\\" or "/" depending on the platform, for example).
        path_parts = path.parts[1:]
    else:
        # Use the parts for the relative path to the root path.
        path_parts = relative_path.parts

    return ".".join(path_parts)


def insert_missing_modules(modules: Dict[str, ModuleType], module_name: str) -> None:
    """
    Used by ``import_path`` to create intermediate modules.
    When we want to import a module as "src.tests.test_foo" for example, we need
    to create empty modules "src" and "src.tests" after inserting "src.tests.test_foo",
    otherwise "src.tests.test_foo" is not importable by ``__import__``.

    Based on: https://github.com/pytest-dev/pytest/blob/main/src/_pytest/pathlib.py
    """
    import importlib

    module_parts = module_name.split(".")
    while module_name:
        if module_name not in modules:
            try:
                # If sys.meta_path is empty, calling import_module will issue
                # a warning and raise ModuleNotFoundError. To avoid the
                # warning, we check sys.meta_path explicitly and raise the error
                # ourselves to fall back to creating a dummy module.
                if not sys.meta_path:
                    raise ModuleNotFoundError
                importlib.import_module(module_name)
            except ModuleNotFoundError:
                module = ModuleType(
                    module_name,
                    doc="Empty module created by robocorp-tasks.",
                )
                modules[module_name] = module
        module_parts.pop(-1)
        module_name = ".".join(module_parts)


def import_path(
    path: Path,
    *,
    root: Path,
) -> ModuleType:
    """Import and return a module from the given path, which can be a file (a module) or
    a directory (a package).

    Based on: https://github.com/pytest-dev/pytest/blob/main/src/_pytest/pathlib.py
    """
    import importlib.util

    if not path.exists():
        raise ImportError(path)

    module_name = module_name_from_path(path, root)

    for meta_importer in sys.meta_path:
        spec = meta_importer.find_spec(module_name, [str(path.parent)])
        if spec is not None:
            break
    else:
        spec = importlib.util.spec_from_file_location(module_name, str(path))

    if spec is None:
        raise ImportError(f"Can't find module {module_name} at location {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    insert_missing_modules(sys.modules, module_name)
    return mod


@contextmanager
def _add_to_sys_path_0(root: Path):
    """
    This context manager may be used to raise priority for some folder so that
    it imports the contents inside it with priority.
    """
    sys.path.insert(0, str(root))
    try:
        yield
    finally:
        try:
            sys.path.remove(str(root))
        except ValueError:
            pass


def collect_tasks(
    path: Path, task_names: Sequence[str] = (), glob: Optional[str] = None
) -> Iterator[ITask]:
    """
    Note: collecting tasks is not thread-safe.
    """
    from robocorp.tasks import _constants, _hooks
    from robocorp.tasks._task import Task

    task_names_as_set = set(task_names)

    _hooks.before_collect_tasks(path, task_names_as_set)

    def accept_task(task: ITask):
        if not task_names:
            return True

        return task.name in task_names

    methods_marked_as_tasks_found: List[Callable] = []
    found_as_set = set()

    def on_func_found(func):
        from robocorp.tasks._exceptions import RobocorpTasksError

        key = (func.__code__.co_name, func.__code__.co_filename)
        if key in found_as_set:
            raise RobocorpTasksError(
                f"Error: a task with the name '{func.__code__.co_name}' was "
                + f"already found in: {func.__code__.co_filename}."
            )
        found_as_set.add(key)

        methods_marked_as_tasks_found.append(func)

    with _hooks.on_task_func_found.register(on_func_found):
        if path.is_dir():
            root = _get_root(path, is_dir=True)
            sys.path.insert(0, str(root))
            with _add_to_sys_path_0(root):
                package_init = path / "__init__.py"
                lst = []
                if package_init.exists():
                    lst.append(package_init)

                use_glob = glob or _constants.DEFAULT_TASK_SEARCH_GLOB

                # We want to accept '|' in glob.
                globs = use_glob.split("|")

                # Use dict to make unique keeping order.
                glob_paths = dict()
                for g in globs:
                    for p in path.rglob(g):
                        glob_paths[p] = 1

                for path_with_task in itertools.chain(lst, tuple(glob_paths.keys())):
                    if path_with_task.is_dir() or not path_with_task.name.endswith(
                        ".py"
                    ):
                        continue

                    module = import_path(path_with_task, root=root)

                    for method in methods_marked_as_tasks_found:
                        task = Task(module, method)
                        if accept_task(task):
                            yield task

                    del methods_marked_as_tasks_found[:]

        elif path.is_file():
            root = _get_root(path, is_dir=False)
            with _add_to_sys_path_0(root):
                module = import_path(path, root=root)
                for method in methods_marked_as_tasks_found:
                    task = Task(module, method)
                    if accept_task(task):
                        yield task

                del methods_marked_as_tasks_found[:]

        else:
            from ._exceptions import RobocorpTasksCollectError

            if not path.exists():
                raise RobocorpTasksCollectError(f"Path: {path} does not exist")

            raise RobocorpTasksCollectError(
                f"Expected {path} to map to a directory or file."
            )


def _get_root(path: Path, is_dir: bool) -> Path:
    pythonpath_entries = tuple(Path(p) for p in sys.path)
    initial = path
    while True:
        # Try to find a parent which is in the pythonpath
        for p in pythonpath_entries:
            try:
                if os.path.samefile(p, path):
                    return p
            except OSError:
                pass

        new_path = path.parent
        if not new_path or new_path == path:
            if is_dir:
                return initial
            else:
                return initial.parent

        path = new_path
