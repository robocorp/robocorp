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

from openapi_client.models.any_valid_json_optional import AnyValidJsonOptional  # noqa: E501

class TestAnyValidJsonOptional(unittest.TestCase):
    """AnyValidJsonOptional unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> AnyValidJsonOptional:
        """Test AnyValidJsonOptional
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `AnyValidJsonOptional`
        """
        model = AnyValidJsonOptional()  # noqa: E501
        if include_optional:
            return AnyValidJsonOptional(
            )
        else:
            return AnyValidJsonOptional(
        )
        """

    def testAnyValidJsonOptional(self):
        """Test AnyValidJsonOptional"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
