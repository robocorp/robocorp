from enum import Enum
from pathlib import Path
from typing import Any, Union

JSONType = Union[dict[str, Any], list[Any], str, int, float, bool, None]
PathType = Union[Path, str]


class State(str, Enum):
    """Work item state. (set when released)"""

    DONE = "COMPLETED"
    FAILED = "FAILED"


class ExceptionType(str, Enum):
    """Failed work item error type."""

    BUSINESS = "BUSINESS"  # wrong/missing data, shouldn't be retried
    APPLICATION = "APPLICATION"  # logic issue/timeout, can be retried
