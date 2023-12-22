from dataclasses import dataclass
from typing import Optional


@dataclass
class TaskOptions:
    is_consequential: Optional[bool] = False
