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

from openapi_client.models.list_processes200_response_data_inner import ListProcesses200ResponseDataInner  # noqa: E501

class TestListProcesses200ResponseDataInner(unittest.TestCase):
    """ListProcesses200ResponseDataInner unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ListProcesses200ResponseDataInner:
        """Test ListProcesses200ResponseDataInner
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `ListProcesses200ResponseDataInner`
        """
        model = ListProcesses200ResponseDataInner()  # noqa: E501
        if include_optional:
            return ListProcesses200ResponseDataInner(
                id = '',
                name = '',
                created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f')
            )
        else:
            return ListProcesses200ResponseDataInner(
                id = '',
                name = '',
                created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
        )
        """

    def testListProcesses200ResponseDataInner(self):
        """Test ListProcesses200ResponseDataInner"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()