from enum import Enum


class State(Enum):
    """Work item state. (set when released)"""

    DONE = "COMPLETED"
    FAILED = "FAILED"


class Error(Enum):
    """Failed work item error type."""

    BUSINESS = "BUSINESS"  # wrong/missing data, shouldn't be retried
    APPLICATION = "APPLICATION"  # logic issue/timeout, can be retried
