from robo import _hooks


def task(func):
    """
    Decorator for tasks (entry points) which can be executed by `robo`.

    i.e.:

    If a file such as tasks.py has the contents below:

    ..
        from robo import task

        @task
        def enter_user():
            ...


    It'll be executable by robo as:

    python -m robo run tasks.py -t enter_user

    Args:
        func: A function which is a task to `robo`.
    """

    # When a task is found, register it in the framework as a target for execution.
    _hooks.on_task_func_found(func)

    return func
