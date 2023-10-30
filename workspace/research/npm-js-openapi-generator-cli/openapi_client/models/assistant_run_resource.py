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

from datetime import datetime
from typing import Optional, Union
from pydantic import BaseModel, Field, StrictFloat, StrictInt, StrictStr, validator
from openapi_client.models.assistant_run_resource_error import AssistantRunResourceError
from openapi_client.models.list_assets200_response_data_inner import ListAssets200ResponseDataInner

class AssistantRunResource(BaseModel):
    """
    AssistantRunResource
    """
    id: StrictStr = Field(...)
    state: StrictStr = Field(...)
    error: Optional[AssistantRunResourceError] = Field(...)
    started_at: datetime = Field(...)
    ended_at: Optional[datetime] = Field(...)
    duration: Optional[Union[StrictFloat, StrictInt]] = Field(...)
    assistant: ListAssets200ResponseDataInner = Field(...)
    __properties = ["id", "state", "error", "started_at", "ended_at", "duration", "assistant"]

    @validator('state')
    def state_validate_enum(cls, value):
        """Validates the enum"""
        if value not in ('in_progress', 'completed', 'failed'):
            raise ValueError("must be one of enum values ('in_progress', 'completed', 'failed')")
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
    def from_json(cls, json_str: str) -> AssistantRunResource:
        """Create an instance of AssistantRunResource from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of error
        if self.error:
            _dict['error'] = self.error.to_dict()
        # override the default output from pydantic by calling `to_dict()` of assistant
        if self.assistant:
            _dict['assistant'] = self.assistant.to_dict()
        # set to None if error (nullable) is None
        # and __fields_set__ contains the field
        if self.error is None and "error" in self.__fields_set__:
            _dict['error'] = None

        # set to None if ended_at (nullable) is None
        # and __fields_set__ contains the field
        if self.ended_at is None and "ended_at" in self.__fields_set__:
            _dict['ended_at'] = None

        # set to None if duration (nullable) is None
        # and __fields_set__ contains the field
        if self.duration is None and "duration" in self.__fields_set__:
            _dict['duration'] = None

        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> AssistantRunResource:
        """Create an instance of AssistantRunResource from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return AssistantRunResource.parse_obj(obj)

        _obj = AssistantRunResource.parse_obj({
            "id": obj.get("id"),
            "state": obj.get("state"),
            "error": AssistantRunResourceError.from_dict(obj.get("error")) if obj.get("error") is not None else None,
            "started_at": obj.get("started_at"),
            "ended_at": obj.get("ended_at"),
            "duration": obj.get("duration"),
            "assistant": ListAssets200ResponseDataInner.from_dict(obj.get("assistant")) if obj.get("assistant") is not None else None
        })
        return _obj

