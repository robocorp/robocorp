# coding: utf-8

"""
    Robocorp Control Room API

    Robocorp Control Room API

    The version of the OpenAPI document: 1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest
import datetime

from workspace.models.assistant_run_resource_error import AssistantRunResourceError  # noqa: E501

class TestAssistantRunResourceError(unittest.TestCase):
    """AssistantRunResourceError unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> AssistantRunResourceError:
        """Test AssistantRunResourceError
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `AssistantRunResourceError`
        """
        model = AssistantRunResourceError()  # noqa: E501
        if include_optional:
            return AssistantRunResourceError(
                code = ''
            )
        else:
            return AssistantRunResourceError(
                code = '',
        )
        """

    def testAssistantRunResourceError(self):
        """Test AssistantRunResourceError"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
