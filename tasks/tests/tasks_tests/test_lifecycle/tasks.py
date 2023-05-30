import itertools

from robocorp.tasks import task, task_cache

_counter = itertools.count()


@task_cache
def new_obj():
    return next(_counter)


@task
def task1():
    assert new_obj() == 0
    assert new_obj() == 0


@task
def task2():
    assert new_obj() == 1
    assert new_obj() == 1
