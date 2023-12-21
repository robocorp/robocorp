from pydantic import BaseModel
from typing import Optional


class TaskOptions(BaseModel):
    is_consequential: Optional[bool] = False
