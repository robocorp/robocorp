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

class WorkItemResource(object):
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
        'created_at': 'datetime',
        'state': 'WorkItemState',
        'state_updated_at': 'datetime',
        'process': 'WorkspacesworkspaceIdworkergroupsworkerGroupIdworkersWorker',
        'process_run': 'WebhookResourceProcess',
        'step': 'WebhookResourceProcess',
        'step_run': 'WebhookResourceProcess',
        'payload': 'WorkItemPayload',
        'files': 'list[WorkItemFile]',
        'exception': 'WorkItemException'
    }

    attribute_map = {
        'id': 'id',
        'created_at': 'created_at',
        'state': 'state',
        'state_updated_at': 'state_updated_at',
        'process': 'process',
        'process_run': 'process_run',
        'step': 'step',
        'step_run': 'step_run',
        'payload': 'payload',
        'files': 'files',
        'exception': 'exception'
    }

    def __init__(self, id=None, created_at=None, state=None, state_updated_at=None, process=None, process_run=None, step=None, step_run=None, payload=None, files=None, exception=None):  # noqa: E501
        """WorkItemResource - a model defined in Swagger"""  # noqa: E501
        self._id = None
        self._created_at = None
        self._state = None
        self._state_updated_at = None
        self._process = None
        self._process_run = None
        self._step = None
        self._step_run = None
        self._payload = None
        self._files = None
        self._exception = None
        self.discriminator = None
        self.id = id
        self.created_at = created_at
        self.state = state
        self.state_updated_at = state_updated_at
        self.process = process
        self.process_run = process_run
        self.step = step
        self.step_run = step_run
        self.payload = payload
        self.files = files
        self.exception = exception

    @property
    def id(self):
        """Gets the id of this WorkItemResource.  # noqa: E501


        :return: The id of this WorkItemResource.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this WorkItemResource.


        :param id: The id of this WorkItemResource.  # noqa: E501
        :type: str
        """
        if id is None:
            raise ValueError("Invalid value for `id`, must not be `None`")  # noqa: E501

        self._id = id

    @property
    def created_at(self):
        """Gets the created_at of this WorkItemResource.  # noqa: E501


        :return: The created_at of this WorkItemResource.  # noqa: E501
        :rtype: datetime
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this WorkItemResource.


        :param created_at: The created_at of this WorkItemResource.  # noqa: E501
        :type: datetime
        """
        if created_at is None:
            raise ValueError("Invalid value for `created_at`, must not be `None`")  # noqa: E501

        self._created_at = created_at

    @property
    def state(self):
        """Gets the state of this WorkItemResource.  # noqa: E501


        :return: The state of this WorkItemResource.  # noqa: E501
        :rtype: WorkItemState
        """
        return self._state

    @state.setter
    def state(self, state):
        """Sets the state of this WorkItemResource.


        :param state: The state of this WorkItemResource.  # noqa: E501
        :type: WorkItemState
        """
        if state is None:
            raise ValueError("Invalid value for `state`, must not be `None`")  # noqa: E501

        self._state = state

    @property
    def state_updated_at(self):
        """Gets the state_updated_at of this WorkItemResource.  # noqa: E501


        :return: The state_updated_at of this WorkItemResource.  # noqa: E501
        :rtype: datetime
        """
        return self._state_updated_at

    @state_updated_at.setter
    def state_updated_at(self, state_updated_at):
        """Sets the state_updated_at of this WorkItemResource.


        :param state_updated_at: The state_updated_at of this WorkItemResource.  # noqa: E501
        :type: datetime
        """
        if state_updated_at is None:
            raise ValueError("Invalid value for `state_updated_at`, must not be `None`")  # noqa: E501

        self._state_updated_at = state_updated_at

    @property
    def process(self):
        """Gets the process of this WorkItemResource.  # noqa: E501


        :return: The process of this WorkItemResource.  # noqa: E501
        :rtype: WorkspacesworkspaceIdworkergroupsworkerGroupIdworkersWorker
        """
        return self._process

    @process.setter
    def process(self, process):
        """Sets the process of this WorkItemResource.


        :param process: The process of this WorkItemResource.  # noqa: E501
        :type: WorkspacesworkspaceIdworkergroupsworkerGroupIdworkersWorker
        """
        if process is None:
            raise ValueError("Invalid value for `process`, must not be `None`")  # noqa: E501

        self._process = process

    @property
    def process_run(self):
        """Gets the process_run of this WorkItemResource.  # noqa: E501


        :return: The process_run of this WorkItemResource.  # noqa: E501
        :rtype: WebhookResourceProcess
        """
        return self._process_run

    @process_run.setter
    def process_run(self, process_run):
        """Sets the process_run of this WorkItemResource.


        :param process_run: The process_run of this WorkItemResource.  # noqa: E501
        :type: WebhookResourceProcess
        """
        if process_run is None:
            raise ValueError("Invalid value for `process_run`, must not be `None`")  # noqa: E501

        self._process_run = process_run

    @property
    def step(self):
        """Gets the step of this WorkItemResource.  # noqa: E501


        :return: The step of this WorkItemResource.  # noqa: E501
        :rtype: WebhookResourceProcess
        """
        return self._step

    @step.setter
    def step(self, step):
        """Sets the step of this WorkItemResource.


        :param step: The step of this WorkItemResource.  # noqa: E501
        :type: WebhookResourceProcess
        """
        if step is None:
            raise ValueError("Invalid value for `step`, must not be `None`")  # noqa: E501

        self._step = step

    @property
    def step_run(self):
        """Gets the step_run of this WorkItemResource.  # noqa: E501


        :return: The step_run of this WorkItemResource.  # noqa: E501
        :rtype: WebhookResourceProcess
        """
        return self._step_run

    @step_run.setter
    def step_run(self, step_run):
        """Sets the step_run of this WorkItemResource.


        :param step_run: The step_run of this WorkItemResource.  # noqa: E501
        :type: WebhookResourceProcess
        """
        if step_run is None:
            raise ValueError("Invalid value for `step_run`, must not be `None`")  # noqa: E501

        self._step_run = step_run

    @property
    def payload(self):
        """Gets the payload of this WorkItemResource.  # noqa: E501


        :return: The payload of this WorkItemResource.  # noqa: E501
        :rtype: WorkItemPayload
        """
        return self._payload

    @payload.setter
    def payload(self, payload):
        """Sets the payload of this WorkItemResource.


        :param payload: The payload of this WorkItemResource.  # noqa: E501
        :type: WorkItemPayload
        """
        if payload is None:
            raise ValueError("Invalid value for `payload`, must not be `None`")  # noqa: E501

        self._payload = payload

    @property
    def files(self):
        """Gets the files of this WorkItemResource.  # noqa: E501


        :return: The files of this WorkItemResource.  # noqa: E501
        :rtype: list[WorkItemFile]
        """
        return self._files

    @files.setter
    def files(self, files):
        """Sets the files of this WorkItemResource.


        :param files: The files of this WorkItemResource.  # noqa: E501
        :type: list[WorkItemFile]
        """
        if files is None:
            raise ValueError("Invalid value for `files`, must not be `None`")  # noqa: E501

        self._files = files

    @property
    def exception(self):
        """Gets the exception of this WorkItemResource.  # noqa: E501


        :return: The exception of this WorkItemResource.  # noqa: E501
        :rtype: WorkItemException
        """
        return self._exception

    @exception.setter
    def exception(self, exception):
        """Sets the exception of this WorkItemResource.


        :param exception: The exception of this WorkItemResource.  # noqa: E501
        :type: WorkItemException
        """
        if exception is None:
            raise ValueError("Invalid value for `exception`, must not be `None`")  # noqa: E501

        self._exception = exception

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
        if issubclass(WorkItemResource, dict):
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
        if not isinstance(other, WorkItemResource):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other