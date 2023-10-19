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

from workspace.models.create_asset_upload200_response import CreateAssetUpload200Response  # noqa: E501

class TestCreateAssetUpload200Response(unittest.TestCase):
    """CreateAssetUpload200Response unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> CreateAssetUpload200Response:
        """Test CreateAssetUpload200Response
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `CreateAssetUpload200Response`
        """
        model = CreateAssetUpload200Response()  # noqa: E501
        if include_optional:
            return CreateAssetUpload200Response(
                id = '',
                status = 'pending',
                content_type = '',
                upload_url = ''
            )
        else:
            return CreateAssetUpload200Response(
                id = '',
                status = 'pending',
                content_type = '',
                upload_url = '',
        )
        """

    def testCreateAssetUpload200Response(self):
        """Test CreateAssetUpload200Response"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
