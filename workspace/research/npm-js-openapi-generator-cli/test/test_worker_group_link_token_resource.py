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

from openapi_client.models.worker_group_link_token_resource import WorkerGroupLinkTokenResource  # noqa: E501

class TestWorkerGroupLinkTokenResource(unittest.TestCase):
    """WorkerGroupLinkTokenResource unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> WorkerGroupLinkTokenResource:
        """Test WorkerGroupLinkTokenResource
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `WorkerGroupLinkTokenResource`
        """
        model = WorkerGroupLinkTokenResource()  # noqa: E501
        if include_optional:
            return WorkerGroupLinkTokenResource(
                id = '',
                name = '',
                expires_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                worker_group = openapi_client.models.add_worker_to_group_request_worker.addWorkerToGroup_request_worker(
                    id = '', )
            )
        else:
            return WorkerGroupLinkTokenResource(
                id = '',
                name = '',
                expires_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                worker_group = openapi_client.models.add_worker_to_group_request_worker.addWorkerToGroup_request_worker(
                    id = '', ),
        )
        """

    def testWorkerGroupLinkTokenResource(self):
        """Test WorkerGroupLinkTokenResource"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
