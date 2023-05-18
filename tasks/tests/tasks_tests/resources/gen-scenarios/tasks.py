# type: ignore
from pathlib import Path
from time import sleep

from robocorp.tasks import task
from contextlib import contextmanager
from somelibrary import call_generators_in_library


def call_method(msg):
    some_assign = msg
    raise RuntimeError(some_assign)


@task
def case_failure():
    """A case which has a known failure"""
    call_method("Error message")


def call_generators():
    yield from range(2)

    for i in range(2):
        yield f"Generated: {i}"


@contextmanager
def check_ctx_manager():
    yield 22


@task
def case_generators():
    """A case which creates generators"""
    for i in call_generators():
        found_var = i

    with check_ctx_manager():
        pass

    for i in call_generators_in_library():
        found_var = i
