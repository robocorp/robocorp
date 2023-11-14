from typing import Tuple

from robocorp.tasks import task


@task
def return_tuple(a: str, b: int, c: str = "") -> Tuple[str, int]:
    assert isinstance(a, str)
    assert isinstance(b, int)
    return a, b


@task
def something_else(f: list) -> None:
    # We can't actually handle this at this point...
    assert isinstance(f, list)


@task
def bool_true(b: bool) -> None:
    assert isinstance(b, bool)
    assert b


@task
def bool_false(b: bool) -> None:
    assert isinstance(b, bool)
    assert not b


@task
def accept_str(s) -> None:
    assert isinstance(s, str)
