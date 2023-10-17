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



from pydantic import BaseModel, Field, StrictStr
from openapi_client.models.create_assistant_request_task import CreateAssistantRequestTask

class CreateAssistantRequest(BaseModel):
    """
    CreateAssistantRequest
    """
    name: StrictStr = Field(...)
    task: CreateAssistantRequestTask = Field(...)
    __properties = ["name", "task"]

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
    def from_json(cls, json_str: str) -> CreateAssistantRequest:
        """Create an instance of CreateAssistantRequest from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of task
        if self.task:
            _dict['task'] = self.task.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> CreateAssistantRequest:
        """Create an instance of CreateAssistantRequest from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return CreateAssistantRequest.parse_obj(obj)

        _obj = CreateAssistantRequest.parse_obj({
            "name": obj.get("name"),
            "task": CreateAssistantRequestTask.from_dict(obj.get("task")) if obj.get("task") is not None else None
        })
        return _obj


