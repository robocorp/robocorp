from robocorp.tasks import _hooks


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

    # When a task is found, register it in the framework as a target for execution.
    _hooks.on_task_func_found(func)

    return func
