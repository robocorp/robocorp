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

from openapi_client.models.generic_error_response import GenericErrorResponse  # noqa: E501

class TestGenericErrorResponse(unittest.TestCase):
    """GenericErrorResponse unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> GenericErrorResponse:
        """Test GenericErrorResponse
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `GenericErrorResponse`
        """
        model = GenericErrorResponse()  # noqa: E501
        if include_optional:
            return GenericErrorResponse(
                error = openapi_client.models.generic_error_response_error.genericErrorResponse_error(
                    code = '', 
                    message = '', )
            )
        else:
            return GenericErrorResponse(
                error = openapi_client.models.generic_error_response_error.genericErrorResponse_error(
                    code = '', 
                    message = '', ),
        )
        """

    def testGenericErrorResponse(self):
        """Test GenericErrorResponse"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
