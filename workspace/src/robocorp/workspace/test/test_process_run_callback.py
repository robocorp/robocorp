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

from workspace.models.process_run_callback import ProcessRunCallback  # noqa: E501

class TestProcessRunCallback(unittest.TestCase):
    """ProcessRunCallback unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ProcessRunCallback:
        """Test ProcessRunCallback
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `ProcessRunCallback`
        """
        model = ProcessRunCallback()  # noqa: E501
        if include_optional:
            return ProcessRunCallback(
                url = '',
                secret = '',
                callback_events = [
                    'started'
                    ]
            )
        else:
            return ProcessRunCallback(
                url = '',
                secret = '',
                callback_events = [
                    'started'
                    ],
        )
        """

    def testProcessRunCallback(self):
        """Test ProcessRunCallback"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
