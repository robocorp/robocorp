from typing import Annotated, Optional, Union

from pydantic import BaseModel, Field
from robocorp.actions import action


class Dependent(BaseModel):
    city: Annotated[str, Field(description="The city.")]


class MyCustomData(BaseModel):
    name: str
    price: Annotated[float, Field(description="This is the price.")]
    is_offer: Union[bool, None] = None
    depends_on: Optional[Dependent] = None


class OutputData(BaseModel):
    accepted: Annotated[bool, Field(description="Was it accepted?.")]
    depends_on: Dependent


@action
def my_action(x: str, data: MyCustomData) -> OutputData:
    assert isinstance(data, MyCustomData)
    return OutputData(accepted=True, depends_on=Dependent(city="Foo"))
