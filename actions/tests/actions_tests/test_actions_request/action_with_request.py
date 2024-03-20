from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field

from robocorp.actions import Request, action


class InputData(BaseModel):
    filename: Annotated[
        str, Field(description="This is the filename to save the value.")
    ]
    price: Annotated[float, Field(description="This is the price.")]


@action
def action_with_request(custom_cls: InputData, request: Request) -> str:
    """
    Args:
        custom_cls: This is the input data.
        request:
    """
    v = request.headers["x-custom-header"]
    Path(custom_cls.filename).write_text(v)
    return v
