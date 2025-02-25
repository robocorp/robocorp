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

from openapi_client.models.workspace_resource import WorkspaceResource  # noqa: E501

class TestWorkspaceResource(unittest.TestCase):
    """WorkspaceResource unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> WorkspaceResource:
        """Test WorkspaceResource
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `WorkspaceResource`
        """
        model = WorkspaceResource()  # noqa: E501
        if include_optional:
            return WorkspaceResource(
                id = '',
                name = '',
                organization = openapi_client.models.list_assets_200_response_data_inner.listAssets_200_response_data_inner(
                    id = '', 
                    name = '', )
            )
        else:
            return WorkspaceResource(
                id = '',
                name = '',
                organization = openapi_client.models.list_assets_200_response_data_inner.listAssets_200_response_data_inner(
                    id = '', 
                    name = '', ),
        )
        """

    def testWorkspaceResource(self):
        """Test WorkspaceResource"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
