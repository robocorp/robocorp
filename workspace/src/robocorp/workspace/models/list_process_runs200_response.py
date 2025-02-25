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
from pydantic import BaseModel
from pydantic import StrictStr, StrictBool
from robocorp.workspace.models.process_run_resource import ProcessRunResource
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

class ListProcessRuns200Response(BaseModel):
    """
    ListProcessRuns200Response
    """ # noqa: E501
    next: Optional[StrictStr]
    has_more: StrictBool
    data: List[ProcessRunResource]
    __properties: ClassVar[List[str]] = ["next", "has_more", "data"]

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
        """Create an instance of ListProcessRuns200Response from a JSON string"""
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
    def from_dict(cls, obj: Dict) -> Self:
        """Create an instance of ListProcessRuns200Response from a dict"""
        if obj is None:
            return None

        if not isinstance(obj, dict):
            return cls.model_validate(obj)

        _obj = cls.model_validate({
            "next": obj.get("next"),
            "has_more": obj.get("has_more"),
            "data": [ProcessRunResource.from_dict(_item) for _item in obj.get("data")] if obj.get("data") is not None else None
        })
        return _obj


