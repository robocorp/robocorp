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

from workspace.models.create_work_item_file200_response import CreateWorkItemFile200Response  # noqa: E501

class TestCreateWorkItemFile200Response(unittest.TestCase):
    """CreateWorkItemFile200Response unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> CreateWorkItemFile200Response:
        """Test CreateWorkItemFile200Response
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `CreateWorkItemFile200Response`
        """
        model = CreateWorkItemFile200Response()  # noqa: E501
        if include_optional:
            return CreateWorkItemFile200Response(
                url = '',
                form_data = None
            )
        else:
            return CreateWorkItemFile200Response(
                url = '',
                form_data = None,
        )
        """

    def testCreateWorkItemFile200Response(self):
        """Test CreateWorkItemFile200Response"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
