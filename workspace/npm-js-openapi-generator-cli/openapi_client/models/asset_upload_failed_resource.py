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



from pydantic import BaseModel, Field, StrictStr, validator

class AssetUploadFailedResource(BaseModel):
    """
    AssetUploadFailedResource
    """
    id: StrictStr = Field(...)
    status: StrictStr = Field(...)
    content_type: StrictStr = Field(...)
    reason: StrictStr = Field(...)
    __properties = ["id", "status", "content_type", "reason"]

    @validator('status')
    def status_validate_enum(cls, value):
        """Validates the enum"""
        if value not in ('failed'):
            raise ValueError("must be one of enum values ('failed')")
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
    def from_json(cls, json_str: str) -> AssetUploadFailedResource:
        """Create an instance of AssetUploadFailedResource from a JSON string"""
        return cls.from_dict(json.loads(json_str))

    def to_dict(self):
        """Returns the dictionary representation of the model using alias"""
        _dict = self.dict(by_alias=True,
                          exclude={
                          },
                          exclude_none=True)
        return _dict

    @classmethod
    def from_dict(cls, obj: dict) -> AssetUploadFailedResource:
        """Create an instance of AssetUploadFailedResource from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return AssetUploadFailedResource.parse_obj(obj)

        _obj = AssetUploadFailedResource.parse_obj({
            "id": obj.get("id"),
            "status": obj.get("status"),
            "content_type": obj.get("content_type"),
            "reason": obj.get("reason")
        })
        return _obj


