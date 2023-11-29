from pathlib import Path
from typing import Optional

from ._fixtures import setup, teardown
from ._protocols import IAction, Status

__version__ = "0.0.1"
version_info = [int(x) for x in __version__.split(".")]


def action(func):
    """
    Decorator for actions (entry points) which can be executed by `robocorp.actions`.

    i.e.:

    If a file such as actions.py has the contents below:

    ```python
    from robocorp.actions import action

    @action
    def enter_user() -> str:
        ...
    ```

    It'll be executable by robocorp actions as:

    python -m robocorp.actions run actions.py -a enter_user

    Args:
        func: A function which is a action to `robocorp.actions`.
    """

    # i.e.: This is just a thin layer for the task decorator at this point
    # (it may be extended in the future...).
    from robocorp.tasks import task

    return task(func)


def session_cache(func):
    """
    Provides decorator which caches return and clears automatically when all
    actions have been run.

    A decorator which automatically cache the result of the given function and
    will return it on any new invocation until robocorp-actions finishes running
    all actions.

    The function may be either a generator with a single yield (so, the first
    yielded value will be returned and when the cache is released the generator
    will be resumed) or a function returning some value.

    Args:
        func: wrapped function.
    """
    from robocorp.tasks import session_cache

    return session_cache(func)


def action_cache(func):
    """
    Provides decorator which caches return and clears it automatically when the
    current action has been run.

    A decorator which automatically cache the result of the given function and
    will return it on any new invocation until robocorp-actions finishes running
    the current action.

    The function may be either a generator with a single yield (so, the first
    yielded value will be returned and when the cache is released the generator
    will be resumed) or a function returning some value.

    Args:
        func: wrapped function.
    """
    from robocorp.tasks import task_cache

    return task_cache(func)


def get_output_dir() -> Optional[Path]:
    """
    Provide the output directory being used for the run or None if there's no
    output dir configured.
    """
    from robocorp.tasks import get_output_dir

    return get_output_dir()


def get_current_action() -> Optional[IAction]:
    """
    Provides the action which is being currently run or None if not currently
    running an action.
    """
    from robocorp.tasks import get_current_task

    return get_current_task()


__all__ = [
    "action",
    "setup",
    "teardown",
    "session_cache",
    "action_cache",
    "get_output_dir",
    "get_current_action",
    "IAction",
    "Status",
]
