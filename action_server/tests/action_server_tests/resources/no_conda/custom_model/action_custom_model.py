from typing import Annotated, Union

from pydantic import BaseModel, Field
from robocorp.actions import action


class MyCustomData(BaseModel):
    name: str
    price: Annotated[float, Field(description="This is the price.")]
    is_offer: Union[bool, None] = None


class OutputData(BaseModel):
    accepted: Annotated[bool, Field(description="Was it accepted?.")]


@action
def my_action(x: str, data: MyCustomData) -> OutputData:
    assert isinstance(data, MyCustomData)
    return OutputData(accepted=True)
