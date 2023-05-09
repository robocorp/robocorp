"""
robocorp-tasks: mark entry points with:

```
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
from pathlib import Path
from typing import Optional
from ._protocols import ITask


__version__ = "0.1.7"
version_info = [int(x) for x in __version__.split(".")]


def task(func):
    """
    Decorator for tasks (entry points) which can be executed by `robocorp.tasks`.

    i.e.:

    If a file such as tasks.py has the contents below:

    ..
        from robocorp.tasks import task

        @task
        def enter_user():
            ...


    It'll be executable by robocorp tasks as:

    python -m robocorp.tasks run tasks.py -t enter_user

    Args:
        func: A function which is a task to `robocorp.tasks`.
    """
    from . import _hooks

    # When a task is found, register it in the framework as a target for execution.
    _hooks.on_task_func_found(func)

    return func


def session_cache(func):
    """
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
    Provide the output directory being used for the run or None if there's
    no output dir configured.
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
