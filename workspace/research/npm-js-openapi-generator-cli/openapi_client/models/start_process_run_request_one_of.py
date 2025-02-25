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


from typing import Optional
from pydantic import BaseModel
from openapi_client.models.process_run_callback import ProcessRunCallback

class StartProcessRunRequestOneOf(BaseModel):
    """
    StartProcessRunRequestOneOf
    """
    callback: Optional[ProcessRunCallback] = None
    __properties = ["callback"]

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
    def from_json(cls, json_str: str) -> StartProcessRunRequestOneOf:
        """Create an instance of StartProcessRunRequestOneOf from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of callback
        if self.callback:
            _dict['callback'] = self.callback.to_dict()
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> StartProcessRunRequestOneOf:
        """Create an instance of StartProcessRunRequestOneOf from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return StartProcessRunRequestOneOf.parse_obj(obj)

        _obj = StartProcessRunRequestOneOf.parse_obj({
            "callback": ProcessRunCallback.from_dict(obj.get("callback")) if obj.get("callback") is not None else None
        })
        return _obj


