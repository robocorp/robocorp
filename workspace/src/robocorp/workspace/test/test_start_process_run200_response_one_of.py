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

from workspace.models.start_process_run200_response_one_of import StartProcessRun200ResponseOneOf  # noqa: E501

class TestStartProcessRun200ResponseOneOf(unittest.TestCase):
    """StartProcessRun200ResponseOneOf unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> StartProcessRun200ResponseOneOf:
        """Test StartProcessRun200ResponseOneOf
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `StartProcessRun200ResponseOneOf`
        """
        model = StartProcessRun200ResponseOneOf()  # noqa: E501
        if include_optional:
            return StartProcessRun200ResponseOneOf(
                started = True
            )
        else:
            return StartProcessRun200ResponseOneOf(
                started = True,
        )
        """

    def testStartProcessRun200ResponseOneOf(self):
        """Test StartProcessRun200ResponseOneOf"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
