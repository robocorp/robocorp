import inspect
from functools import wraps
from typing import Callable, Literal, TypeVar, Union, overload

from ._protocols import ITaskCallback, ITasksCallback

T = TypeVar("T")
Decorator = Callable[[T], T]


@overload
def setup(func: ITaskCallback) -> ITaskCallback:
    ...


@overload
def setup(*, scope: Literal["task"] = "task") -> Decorator[ITaskCallback]:
    ...


@overload
def setup(*, scope: Literal["session"]) -> Decorator[ITasksCallback]:
    ...


def setup(
    *args, **kwargs
) -> Union[ITaskCallback, Decorator[ITaskCallback], Decorator[ITasksCallback]]:
    """Run code before any tasks start, or before each separate task.

    Receives as an argument the task or tasks that will be run.

    Can be used as a decorator without arguments:

    ```python
    from robocorp.tasks import setup

    @setup
    def my_fixture(task):
        print(f"Before task: {task.name}")
    ```

    Alternatively, can be called with a `scope` argument to decide when
    the fixture is run:

    ```python
    from robocorp.tasks import setup

    @setup(scope="task")
    def before_each(task):
        print(f"Running task '{task.name}'")

    @setup(scope="session")
    def before_all(tasks):
        print(f"Running {len(tasks)} task(s)")
    ```

    By default, runs setups in `task` scope.

    The `setup` fixture also allows running code after the execution,
    if it `yield`s the execution to the task(s):

    ```python
    import time
    from robocorp.tasks import setup

    @setup
    def measure_time(task):
        start = time.time()
        yield  # Task executes here
        duration = time.time() - start
        print(f"Task took {duration} seconds")

    @task
    def my_long_task():
        ...
    ```

    **Note:** If fixtures are defined in another file, they need to be imported
     in the main tasks file to be taken into use
    """
    from ._hooks import (
        after_all_tasks_run,
        after_task_run,
        before_all_tasks_run,
        before_task_run,
    )

    def _register_callback(before, after, func):
        if inspect.isgeneratorfunction(func):

            @wraps(func)
            def generator(*args, **kwargs):
                gen = func(*args, **kwargs)
                next(gen)

                def teardown(*args, **kwargs):
                    try:
                        next(gen)
                    except StopIteration:
                        pass
                    finally:
                        after.unregister(teardown)

                after.register(teardown)

            before.register(generator)
            return generator
        else:
            before.register(func)
            return func

    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        return _register_callback(before_task_run, after_task_run, args[0])

    scope = kwargs.get("scope", "task")
    if scope == "task":

        def wrapped_task(func):
            return _register_callback(before_task_run, after_task_run, func)

        return wrapped_task
    elif scope == "session":

        def wrapped_session(func):
            return _register_callback(before_all_tasks_run, after_all_tasks_run, func)

        return wrapped_session
    else:
        raise ValueError(f"Unknown scope '{scope}', expected 'task' or 'session'")


@overload
def teardown(func: ITaskCallback) -> ITaskCallback:
    ...


@overload
def teardown(*, scope: Literal["task"] = "task") -> Decorator[ITaskCallback]:
    ...


@overload
def teardown(*, scope: Literal["session"]) -> Decorator[ITasksCallback]:
    ...


def teardown(
    *args, **kwargs
) -> Union[ITaskCallback, Decorator[ITaskCallback], Decorator[ITasksCallback]]:
    """Run code after tasks have been run, or after each separate task.

    Receives as an argument the task or tasks that were executed, which
    contain (among other things) the resulting status and possible error message.

    Can be used as a decorator without arguments:

    ```python
    from robocorp.tasks import teardown

    @teardown
    def my_fixture(task):
        print(f"After task: {task.name})
    ```

    Alternatively, can be called with a `scope` argument to decide when
    the fixture is run:

    ```python
    from robocorp.tasks import teardown

    @teardown(scope="task")
    def after_each(task):
        print(f"Task '{task.name}' status is '{task.status}'")

    @teardown(scope="session")
    def after_all(tasks):
        print(f"Executed {len(tasks)} task(s)")
    ```

    By default, runs teardowns in `task` scope.

    **Note:** If fixtures are defined in another file, they need to be imported
     in the main tasks file to be taken into use
    """
    from ._hooks import after_all_tasks_run, after_task_run

    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        func: ITaskCallback = args[0]
        after_task_run.register(func)
        return func

    scope = kwargs.get("scope", "task")
    if scope == "task":

        def wrapped_task(func: ITaskCallback):
            after_task_run.register(func)
            return func

        return wrapped_task
    elif scope == "session":

        def wrapped_session(func: ITasksCallback):
            after_all_tasks_run.register(func)
            return func

        return wrapped_session
    else:
        raise ValueError(f"Unknown scope '{scope}', expected 'task' or 'session'")
