from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union

from dataclasses_json import LetterCase, config, dataclass_json
from dateutil.parser import isoparse
from marshmallow import fields

JSONType = Union[dict[str, Any], list[Any], str, int, float, bool, None]
PathType = Union[Path, str]


class State(str, Enum):
    """Work item state, after release."""

    DONE = "COMPLETED"
    FAILED = "FAILED"


class ExceptionType(str, Enum):
    """Failed work item error type."""

    BUSINESS = "BUSINESS"  # wrong/missing data, shouldn't be retried
    APPLICATION = "APPLICATION"  # logic issue/timeout, can be retried


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Address:
    name: str
    address: str


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Email:
    """Container for Email attached to work item."""

    # Unable to use "from" as attribute as it is a reserved word
    from_: Address = field(metadata=config(field_name="from"))
    to: list[Address]
    cc: list[Address]
    bcc: list[Address]
    reply_to: Address

    subject: str
    date: datetime = field(
        metadata={
            "dataclasses_json": {
                "encoder": datetime.isoformat,
                "decoder": isoparse,
                "mm_field": fields.DateTime(format="iso"),
            }
        }
    )

    text: Optional[str] = None
    html: Optional[str] = None

    errors: list[str] = field(default_factory=list)
