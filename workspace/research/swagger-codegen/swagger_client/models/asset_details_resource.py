# coding: utf-8

"""
    Robocorp Control Room API

    Robocorp Control Room API  # noqa: E501

    OpenAPI spec version: 1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

import pprint
import re  # noqa: F401

import six

class AssetDetailsResource(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'id': 'str',
        'name': 'str',
        'payload': 'OneOfAssetDetailsResourcePayload'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'payload': 'payload'
    }

    def __init__(self, id=None, name=None, payload=None):  # noqa: E501
        """AssetDetailsResource - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._name = None
        self._payload = None
        self.discriminator = None
        self.id = id
        self.name = name
        self.payload = payload

    @property
    def id(self):
        """Gets the id of this AssetDetailsResource.  # noqa: E501


        :return: The id of this AssetDetailsResource.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this AssetDetailsResource.


        :param id: The id of this AssetDetailsResource.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def name(self):
        """Gets the name of this AssetDetailsResource.  # noqa: E501


        :return: The name of this AssetDetailsResource.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this AssetDetailsResource.


        :param name: The name of this AssetDetailsResource.  # noqa: E501
        :type: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def payload(self):
        """Gets the payload of this AssetDetailsResource.  # noqa: E501


        :return: The payload of this AssetDetailsResource.  # noqa: E501
        :rtype: OneOfAssetDetailsResourcePayload
        """
        return self._payload

    @payload.setter
    def payload(self, payload):
        """Sets the payload of this AssetDetailsResource.


        :param payload: The payload of this AssetDetailsResource.  # noqa: E501
        :type: OneOfAssetDetailsResourcePayload
        """
        if payload is None:
            raise ValueError("Invalid value for `payload`, must not be `None`")  # noqa: E501

        self._payload = payload

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(AssetDetailsResource, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, AssetDetailsResource):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
