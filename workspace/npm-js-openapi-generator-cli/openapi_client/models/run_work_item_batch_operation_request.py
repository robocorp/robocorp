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


from typing import List
from pydantic import BaseModel, Field, StrictStr, conlist, validator

class RunWorkItemBatchOperationRequest(BaseModel):
    """
    RunWorkItemBatchOperationRequest
    """
    batch_operation: StrictStr = Field(...)
    work_item_ids: conlist(StrictStr) = Field(...)
    __properties = ["batch_operation", "work_item_ids"]

    @validator('batch_operation')
    def batch_operation_validate_enum(cls, value):
        """Validates the enum"""
        if value not in ('retry', 'delete', 'mark_as_done'):
            raise ValueError("must be one of enum values ('retry', 'delete', 'mark_as_done')")
        return value

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        validate_assignment = True

    def to_str(self) -> str:
        """Returns the string representation of the model using alias"""
        return pprint.pformat(self.dict(by_alias=True))

    def to_json(self) -> str:
        """Returns the JSON representation of the model using alias"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> RunWorkItemBatchOperationRequest:
        """Create an instance of RunWorkItemBatchOperationRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> RunWorkItemBatchOperationRequest:
        """Create an instance of RunWorkItemBatchOperationRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return RunWorkItemBatchOperationRequest.parse_obj(obj)

        _obj = RunWorkItemBatchOperationRequest.parse_obj({
            "batch_operation": obj.get("batch_operation"),
            "work_item_ids": obj.get("work_item_ids")
        })
        return _obj


