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

from openapi_client.models.process_reference_resource import ProcessReferenceResource  # noqa: E501

class TestProcessReferenceResource(unittest.TestCase):
    """ProcessReferenceResource unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ProcessReferenceResource:
        """Test ProcessReferenceResource
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `ProcessReferenceResource`
        """
        model = ProcessReferenceResource()  # noqa: E501
        if include_optional:
            return ProcessReferenceResource(
                id = ''
            )
        else:
            return ProcessReferenceResource(
                id = '',
        )
        """

    def testProcessReferenceResource(self):
        """Test ProcessReferenceResource"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()