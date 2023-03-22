from robo import _hooks


def task(func):
    _hooks.on_task_func_found(func)

    return func
