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

from workspace.models.work_item_without_data_resource import WorkItemWithoutDataResource  # noqa: E501

class TestWorkItemWithoutDataResource(unittest.TestCase):
    """WorkItemWithoutDataResource unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> WorkItemWithoutDataResource:
        """Test WorkItemWithoutDataResource
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `WorkItemWithoutDataResource`
        """
        model = WorkItemWithoutDataResource()  # noqa: E501
        if include_optional:
            return WorkItemWithoutDataResource(
                id = '',
                created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                state = 'new',
                state_updated_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                process = workspace.models.add_worker_to_group_request_worker.addWorkerToGroup_request_worker(
                    id = '', ),
                process_run = workspace.models.list_webhooks_200_response_data_inner_process.listWebhooks_200_response_data_inner_process(
                    id = '', ),
                step = workspace.models.list_webhooks_200_response_data_inner_process.listWebhooks_200_response_data_inner_process(
                    id = '', ),
                step_run = workspace.models.list_webhooks_200_response_data_inner_process.listWebhooks_200_response_data_inner_process(
                    id = '', ),
                exception = workspace.models.work_item_exception.WorkItemException(
                    code = '', 
                    type = 'application', 
                    message = '', )
            )
        else:
            return WorkItemWithoutDataResource(
                id = '',
                created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                state = 'new',
                state_updated_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                process = workspace.models.add_worker_to_group_request_worker.addWorkerToGroup_request_worker(
                    id = '', ),
                process_run = workspace.models.list_webhooks_200_response_data_inner_process.listWebhooks_200_response_data_inner_process(
                    id = '', ),
                step = workspace.models.list_webhooks_200_response_data_inner_process.listWebhooks_200_response_data_inner_process(
                    id = '', ),
                step_run = workspace.models.list_webhooks_200_response_data_inner_process.listWebhooks_200_response_data_inner_process(
                    id = '', ),
                exception = workspace.models.work_item_exception.WorkItemException(
                    code = '', 
                    type = 'application', 
                    message = '', ),
        )
        """

    def testWorkItemWithoutDataResource(self):
        """Test WorkItemWithoutDataResource"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
