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

from openapi_client.models.start_process_run200_response import StartProcessRun200Response  # noqa: E501

class TestStartProcessRun200Response(unittest.TestCase):
    """StartProcessRun200Response unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> StartProcessRun200Response:
        """Test StartProcessRun200Response
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `StartProcessRun200Response`
        """
        model = StartProcessRun200Response()  # noqa: E501
        if include_optional:
            return StartProcessRun200Response(
                started = True,
                id = ''
            )
        else:
            return StartProcessRun200Response(
                started = True,
                id = '',
        )
        """

    def testStartProcessRun200Response(self):
        """Test StartProcessRun200Response"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
