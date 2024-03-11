from typing import Annotated, Tuple, Union

from pydantic import BaseModel, Field

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


@task
def unicode_ação_Σ(ação: str) -> None:
    assert isinstance(ação, str)


class MyCustomData(BaseModel):
    name: str
    price: Annotated[float, Field(description="This is the price.")]
    is_offer: Union[bool, None] = None


@task
def custom_data(data: MyCustomData) -> None:
    assert isinstance(data, MyCustomData)
