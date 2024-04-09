"""Robocorp tasks helps in creating entry points for your automation project.

To use:

Mark entry points with:

```
from robocorp.tasks import task

@task
def my_method():
    ...
```

Running options:

Runs all the tasks in a .py file:

  `python -m robocorp.tasks run <path_to_file>`

Run all the tasks in files named *task*.py:

  `python -m robocorp.tasks run <directory>`

Run only tasks with a given name:

  `python -m robocorp.tasks run <directory or file> -t <task_name>`


Note: Using the `cli.main(args)` is possible to run tasks programmatically, but
clients using this approach MUST make sure that any code which must be
automatically logged is not imported prior the the `cli.main` call.
"""
from functools import wraps
from pathlib import Path
from typing import Dict, Optional

from ._fixtures import setup, teardown
from ._protocols import ITask, Status

__version__ = "3.0.3"
version_info = [int(x) for x in __version__.split(".")]


def task(*args, **kwargs):
    """
    Decorator for tasks (entry points) which can be executed by `robocorp.tasks`.

    i.e.:

    If a file such as tasks.py has the contents below:

    ```python
    from robocorp.tasks import task

    @task
    def enter_user():
        ...
    ```

    It's also possible to pass options to the task decorator that can then be introspected by `task.options`:

    ```python
    from robocorp.tasks import task

    @task(this_is_option="option")
    def enter_user():
        ...
    ```

    It'll be executable by robocorp tasks as:

    python -m robocorp.tasks run tasks.py -t enter_user

    Args:
        func: A function which is a task to `robocorp.tasks`.
        **kwargs: Options to be introspected by `task.options`.
    """

    def decorator(func, options: Optional[Dict] = None):
        from . import _hooks

        # When a task is found, register it in the framework as a target for execution.
        _hooks.on_task_func_found(func, options=options)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    if args and callable(args[0]):
        return decorator(args[0], options=kwargs)

    return lambda func: decorator(func, options=kwargs)


def session_cache(func):
    """
    Provides decorator which caches return and clears automatically when all
    tasks have been run.

    A decorator which automatically cache the result of the given function and
    will return it on any new invocation until robocorp-tasks finishes running
    all tasks.

    The function may be either a generator with a single yield (so, the first
    yielded value will be returned and when the cache is released the generator
    will be resumed) or a function returning some value.

    Args:
        func: wrapped function.
    """
    from ._hooks import after_all_tasks_run
    from ._lifecycle import _cache

    return _cache(after_all_tasks_run, func)


def task_cache(func):
    """
    Provides decorator which caches return and clears it automatically when the
    current task has been run.

    A decorator which automatically cache the result of the given function and
    will return it on any new invocation until robocorp-tasks finishes running
    the current task.

    The function may be either a generator with a single yield (so, the first
    yielded value will be returned and when the cache is released the generator
    will be resumed) or a function returning some value.

    Args:
        func: wrapped function.
    """
    from ._hooks import after_task_run
    from ._lifecycle import _cache

    return _cache(after_task_run, func)


def get_output_dir() -> Optional[Path]:
    """
    Provide the output directory being used for the run or None if there's no
    output dir configured.
    """
    from ._config import get_config

    config = get_config()
    if config is None:
        return None
    return config.output_dir


def get_current_task() -> Optional[ITask]:
    """
    Provides the task which is being currently run or None if not currently
    running a task.
    """
    from . import _task

    return _task.get_current_task()


__all__ = [
    "task",
    "setup",
    "teardown",
    "session_cache",
    "task_cache",
    "get_output_dir",
    "get_current_task",
    "ITask",
    "Status",
]
