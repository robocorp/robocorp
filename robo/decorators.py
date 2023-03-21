from robo._callback import Callback

on_task_found = Callback()


def task(func):
    on_task_found(func)

    return func
