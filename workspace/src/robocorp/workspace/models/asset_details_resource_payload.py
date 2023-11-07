# coding: utf-8

"""
    Robocorp Control Room API

    Robocorp Control Room API

    The version of the OpenAPI document: 1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


from __future__ import annotations
from inspect import getfullargspec
import json
import pprint
import re  # noqa: F401

from typing import Any, List, Optional
from pydantic import BaseModel, Field, StrictStr, ValidationError, field_validator
from robocorp.workspace.models.asset_payload_empty_resource import AssetPayloadEmptyResource
from robocorp.workspace.models.asset_payload_url_resource import AssetPayloadUrlResource
from typing import Union, Any, List, TYPE_CHECKING, Optional, Dict
from typing_extensions import Literal
from pydantic import StrictStr, Field
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

ASSETDETAILSRESOURCEPAYLOAD_ONE_OF_SCHEMAS = ["AssetPayloadEmptyResource", "AssetPayloadUrlResource"]

class AssetDetailsResourcePayload(BaseModel):
    """
    AssetDetailsResourcePayload
    """
    # data type: AssetPayloadEmptyResource
    oneof_schema_1_validator: Optional[AssetPayloadEmptyResource] = None
    # data type: AssetPayloadUrlResource
    oneof_schema_2_validator: Optional[AssetPayloadUrlResource] = None
    actual_instance: Optional[Union[AssetPayloadEmptyResource, AssetPayloadUrlResource]] = None
    one_of_schemas: List[str] = Literal["AssetPayloadEmptyResource", "AssetPayloadUrlResource"]

    model_config = {
        "validate_assignment": True
    }


    def __init__(self, *args, **kwargs) -> None:
        if args:
            if len(args) > 1:
                raise ValueError("If a position argument is used, only 1 is allowed to set `actual_instance`")
            if kwargs:
                raise ValueError("If a position argument is used, keyword arguments cannot be used.")
            super().__init__(actual_instance=args[0])
        else:
            super().__init__(**kwargs)

    @field_validator('actual_instance')
    def actual_instance_must_validate_oneof(cls, v):
        instance = AssetDetailsResourcePayload.model_construct()
        error_messages = []
        match = 0
        # validate data type: AssetPayloadEmptyResource
        if not isinstance(v, AssetPayloadEmptyResource):
            error_messages.append(f"Error! Input type `{type(v)}` is not `AssetPayloadEmptyResource`")
        else:
            match += 1
        # validate data type: AssetPayloadUrlResource
        if not isinstance(v, AssetPayloadUrlResource):
            error_messages.append(f"Error! Input type `{type(v)}` is not `AssetPayloadUrlResource`")
        else:
            match += 1
        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when setting `actual_instance` in AssetDetailsResourcePayload with oneOf schemas: AssetPayloadEmptyResource, AssetPayloadUrlResource. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when setting `actual_instance` in AssetDetailsResourcePayload with oneOf schemas: AssetPayloadEmptyResource, AssetPayloadUrlResource. Details: " + ", ".join(error_messages))
        else:
            return v

    @classmethod
    def from_dict(cls, obj: dict) -> Self:
        return cls.from_json(json.dumps(obj))

    @classmethod
    def from_json(cls, json_str: str) -> Self:
        """Returns the object represented by the json string"""
        instance = cls.model_construct()
        error_messages = []
        match = 0

        # deserialize data into AssetPayloadEmptyResource
        try:
            instance.actual_instance = AssetPayloadEmptyResource.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))
        # deserialize data into AssetPayloadUrlResource
        try:
            instance.actual_instance = AssetPayloadUrlResource.from_json(json_str)
            match += 1
        except (ValidationError, ValueError) as e:
            error_messages.append(str(e))

        if match > 1:
            # more than 1 match
            raise ValueError("Multiple matches found when deserializing the JSON string into AssetDetailsResourcePayload with oneOf schemas: AssetPayloadEmptyResource, AssetPayloadUrlResource. Details: " + ", ".join(error_messages))
        elif match == 0:
            # no match
            raise ValueError("No match found when deserializing the JSON string into AssetDetailsResourcePayload with oneOf schemas: AssetPayloadEmptyResource, AssetPayloadUrlResource. Details: " + ", ".join(error_messages))
        else:
            return instance

    def to_json(self) -> str:
        """Returns the JSON representation of the actual instance"""
        if self.actual_instance is None:
            return "null"

        to_json = getattr(self.actual_instance, "to_json", None)
        if callable(to_json):
            return self.actual_instance.to_json()
        else:
            return json.dumps(self.actual_instance)

    def to_dict(self) -> dict:
        """Returns the dict representation of the actual instance"""
        if self.actual_instance is None:
            return None

        to_dict = getattr(self.actual_instance, "to_dict", None)
        if callable(to_dict):
            return self.actual_instance.to_dict()
        else:
            # primitive type
            return self.actual_instance

    def to_str(self) -> str:
        """Returns the string representation of the actual instance"""
        return pprint.pformat(self.model_dump())


