# type: ignore
from pathlib import Path
from time import sleep

from robocorp.tasks import task


def call_method(msg):
    some_assign = msg
    raise RuntimeError(some_assign)


@task
def case_failure():
    """A case which has a known failure"""
    call_method("Error message")
