# coding: utf-8

"""
    Robocorp Control Room API

    Robocorp Control Room API

    The version of the OpenAPI document: 1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
import pprint
import re  # noqa: F401
import json


from typing import Any, ClassVar, Dict, List
from typing import Optional
from pydantic import BaseModel, StrictStr, field_validator
from pydantic import StrictStr, StrictBool
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class RunWorkItemBatchOperationRequest(BaseModel):
    """
    RunWorkItemBatchOperationRequest
    """ # noqa: E501
    batch_operation: StrictStr
    work_item_ids: List[StrictStr]
    __properties: ClassVar[List[str]] = ["batch_operation", "work_item_ids"]

    @field_validator('batch_operation')
    def batch_operation_validate_enum(cls, value):
        """Validates the enum"""
        if value not in ('retry', 'delete', 'mark_as_done'):
            raise ValueError("must be one of enum values ('retry', 'delete', 'mark_as_done')")
        return value

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True
    }


    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.model_dump(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        # TODO: pydantic v2: use .model_dump_json(by_alias=True, exclude_unset=True) instead
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Create an instance of RunWorkItemBatchOperationRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self) -> Dict[str, Any]:
        """Return the dictionary representation of the model using alias.

        This has the following differences from calling pydantic's
        `self.model_dump(by_alias=True)`:

        * `None` is only added to the output dict for nullable fields that
          were set at model initialization. Other fields with value `None`
          are ignored.
        """
        _dict = self.model_dump(
            by_alias=True,
            exclude={
            },
            exclude_none=True,
        )
        return _dict

    @classmethod
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of RunWorkItemBatchOperationRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "batch_operation": obj.get("batch_operation"),
            "work_item_ids": obj.get("work_item_ids")
        })
        return _obj


