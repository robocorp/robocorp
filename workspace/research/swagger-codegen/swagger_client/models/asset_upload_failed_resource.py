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

class AssetUploadFailedResource(object):
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
        'status': 'str',
        'content_type': 'AssetPayloadContentType',
        'reason': 'str'
    }

    attribute_map = {
        'id': 'id',
        'status': 'status',
        'content_type': 'content_type',
        'reason': 'reason'
    }

    def __init__(self, id=None, status=None, content_type=None, reason=None):  # noqa: E501
        """AssetUploadFailedResource - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._status = None
        self._content_type = None
        self._reason = None
        self.discriminator = None
        self.id = id
        self.status = status
        self.content_type = content_type
        self.reason = reason

    @property
    def id(self):
        """Gets the id of this AssetUploadFailedResource.  # noqa: E501


        :return: The id of this AssetUploadFailedResource.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this AssetUploadFailedResource.


        :param id: The id of this AssetUploadFailedResource.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def status(self):
        """Gets the status of this AssetUploadFailedResource.  # noqa: E501


        :return: The status of this AssetUploadFailedResource.  # noqa: E501
        :rtype: str
        """
        return self._status

    @status.setter
    def status(self, status):
        """Sets the status of this AssetUploadFailedResource.


        :param status: The status of this AssetUploadFailedResource.  # noqa: E501
        :type: str
        """
        if status is None:
            raise ValueError("Invalid value for `status`, must not be `None`")  # noqa: E501
        allowed_values = ["failed"]  # noqa: E501
        if status not in allowed_values:
            raise ValueError(
                "Invalid value for `status` ({0}), must be one of {1}"  # noqa: E501
                .format(status, allowed_values)
            )

        self._status = status

    @property
    def content_type(self):
        """Gets the content_type of this AssetUploadFailedResource.  # noqa: E501


        :return: The content_type of this AssetUploadFailedResource.  # noqa: E501
        :rtype: AssetPayloadContentType
        """
        return self._content_type

    @content_type.setter
    def content_type(self, content_type):
        """Sets the content_type of this AssetUploadFailedResource.


        :param content_type: The content_type of this AssetUploadFailedResource.  # noqa: E501
        :type: AssetPayloadContentType
        """
        if content_type is None:
            raise ValueError("Invalid value for `content_type`, must not be `None`")  # noqa: E501

        self._content_type = content_type

    @property
    def reason(self):
        """Gets the reason of this AssetUploadFailedResource.  # noqa: E501


        :return: The reason of this AssetUploadFailedResource.  # noqa: E501
        :rtype: str
        """
        return self._reason

    @reason.setter
    def reason(self, reason):
        """Sets the reason of this AssetUploadFailedResource.


        :param reason: The reason of this AssetUploadFailedResource.  # noqa: E501
        :type: str
        """
        if reason is None:
            raise ValueError("Invalid value for `reason`, must not be `None`")  # noqa: E501

        self._reason = reason

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
        if issubclass(AssetUploadFailedResource, dict):
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
        if not isinstance(other, AssetUploadFailedResource):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
