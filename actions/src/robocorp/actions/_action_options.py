from dataclasses import dataclass
from typing import Optional


@dataclass
class ActionOptions:
    is_consequential: Optional[bool] = None
