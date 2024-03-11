# Dealing with custom data models

Starting with `robocorp-actions 0.0.8` and `Action Server 0.0.28`, custom
pydantic models may be used to define a schema containing complex objects as
the input/output of a an `@action`.

-- previous versions supported just `str`, `int`, `float`, `bool`.

## Example

To define a custom data model, pydantic classes must be used to define the shape
of the data. 

Below is an example which defines an `@action` with a custom input and output:

```
from typing import Annotated

from pydantic import BaseModel, Field
from robocorp.actions import action

class InputData(BaseModel):
    name: Annotated[str, Field(description="This is the name.")]
    price: Annotated[float, Field(description="This is the price.")]

class OutputData(BaseModel):
    accept_input: Annotated[bool, Field(description="Defines whether the input was accepted.")]

@action
def accept_data(data: InputData) -> OutputData:
    assert isinstance(data, InputData)
    return OutputData(accept_input=data.price < 100)
```

## Note

Note: `pydantic` is not really a hard dependency of `robocorp-actions` and must
be included as a custom dependency in projects that require custom data models
as `robocorp-actions` just uses duck-typing to check for the APIs below: 

- `cls.model_validate(dict)` 
- `cls.model_json_schema()`
- `obj.model_dump_json()`

 -- in theory it'd be even possible to define a custom model that doesn't 
 really depend on pydantic, although the replacement would need to follow the 
 same semantics for those methods.
