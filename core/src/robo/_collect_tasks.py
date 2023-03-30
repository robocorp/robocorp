from pathlib import Path
from typing import Iterator, List, Callable, Dict
from types import ModuleType
import sys
from robo._protocols import ITask


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
    Used by ``import_path`` to create intermediate modules when using mode=importlib.
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
                    doc="Empty module created by pytest's importmode=importlib.",
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


def collect_tasks(path: Path, task_name: str = "") -> Iterator[ITask]:
    """
    Note: collecting tasks is not thread-safe.
    """
    from robo import _hooks
    from robo._task import Task

    _hooks.before_collect_tasks(path, task_name)

    def accept_task(task: ITask):
        if not task_name:
            return True

        return task.name == task_name

    methods_marked_as_tasks_found: List[Callable] = []

    _hooks.on_task_func_found.register(methods_marked_as_tasks_found.append)

    try:
        if path.is_dir():
            for path_with_task in path.rglob("*task*.py"):
                module = import_path(path_with_task, root=path)

                for method in methods_marked_as_tasks_found:
                    task = Task(module, method)
                    if accept_task(task):
                        yield task

                del methods_marked_as_tasks_found[:]

        elif path.is_file():
            module = import_path(path, root=path.parent)
            for method in methods_marked_as_tasks_found:
                task = Task(module, method)
                if accept_task(task):
                    yield task

            del methods_marked_as_tasks_found[:]

        else:
            from ._exceptions import RoboCollectError

            if not path.exists():
                raise RoboCollectError(f"Path: {path} does not exist")

            raise RoboCollectError(f"Expected {path} to map to a directory or file.")
    finally:
        _hooks.on_task_func_found.unregister(methods_marked_as_tasks_found.append)
