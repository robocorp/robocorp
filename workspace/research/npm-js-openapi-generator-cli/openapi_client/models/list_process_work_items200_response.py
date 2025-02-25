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
from pydantic import BaseModel, Field, conlist
from openapi_client.models.work_item_without_data_resource import WorkItemWithoutDataResource

class ListProcessWorkItems200Response(BaseModel):
    """
    ListProcessWorkItems200Response
    """
    next: Next = Field(...)
    has_more: HasMore = Field(...)
    data: conlist(WorkItemWithoutDataResource) = Field(...)
    __properties = ["next", "has_more", "data"]

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
    def from_json(cls, json_str: str) -> ListProcessWorkItems200Response:
        """Create an instance of ListProcessWorkItems200Response from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        # override the default output from pydantic by calling `to_dict()` of next
        if self.next:
            _dict['next'] = self.next.to_dict()
        # override the default output from pydantic by calling `to_dict()` of has_more
        if self.has_more:
            _dict['has_more'] = self.has_more.to_dict()
        # override the default output from pydantic by calling `to_dict()` of each item in data (list)
        _items = []
        if self.data:
            for _item in self.data:
                if _item:
                    _items.append(_item.to_dict())
            _dict['data'] = _items
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> ListProcessWorkItems200Response:
        """Create an instance of ListProcessWorkItems200Response from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return ListProcessWorkItems200Response.parse_obj(obj)

        _obj = ListProcessWorkItems200Response.parse_obj({
            "next": Next.from_dict(obj.get("next")) if obj.get("next") is not None else None,
            "has_more": HasMore.from_dict(obj.get("has_more")) if obj.get("has_more") is not None else None,
            "data": [WorkItemWithoutDataResource.from_dict(_item) for _item in obj.get("data")] if obj.get("data") is not None else None
        })
        return _obj


