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

from openapi_client.models.list_process_run_work_items200_response_data_inner import ListProcessRunWorkItems200ResponseDataInner  # noqa: E501

class TestListProcessRunWorkItems200ResponseDataInner(unittest.TestCase):
    """ListProcessRunWorkItems200ResponseDataInner unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ListProcessRunWorkItems200ResponseDataInner:
        """Test ListProcessRunWorkItems200ResponseDataInner
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `ListProcessRunWorkItems200ResponseDataInner`
        """
        model = ListProcessRunWorkItems200ResponseDataInner()  # noqa: E501
        if include_optional:
            return ListProcessRunWorkItems200ResponseDataInner(
                id = '',
                created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                state = 'pending',
                state_updated_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                process = openapi_client.models.add_worker_to_group_request_worker.addWorkerToGroup_request_worker(
                    id = '', ),
                process_run = openapi_client.models.add_worker_to_group_request_worker.addWorkerToGroup_request_worker(
                    id = '', ),
                step = openapi_client.models.add_worker_to_group_request_worker.addWorkerToGroup_request_worker(
                    id = '', ),
                step_run = openapi_client.models.list_process_run_work_items_200_response_data_inner_step_run.listProcessRunWorkItems_200_response_data_inner_step_run(
                    id = '', ),
                exception = openapi_client.models.work_item_exception.WorkItemException(
                    code = '', 
                    type = 'application', 
                    message = '', )
            )
        else:
            return ListProcessRunWorkItems200ResponseDataInner(
                id = '',
                created_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                state = 'pending',
                state_updated_at = datetime.datetime.strptime('2013-10-20 19:20:30.00', '%Y-%m-%d %H:%M:%S.%f'),
                process = openapi_client.models.add_worker_to_group_request_worker.addWorkerToGroup_request_worker(
                    id = '', ),
                process_run = openapi_client.models.add_worker_to_group_request_worker.addWorkerToGroup_request_worker(
                    id = '', ),
                step = openapi_client.models.add_worker_to_group_request_worker.addWorkerToGroup_request_worker(
                    id = '', ),
                step_run = openapi_client.models.list_process_run_work_items_200_response_data_inner_step_run.listProcessRunWorkItems_200_response_data_inner_step_run(
                    id = '', ),
                exception = openapi_client.models.work_item_exception.WorkItemException(
                    code = '', 
                    type = 'application', 
                    message = '', ),
        )
        """

    def testListProcessRunWorkItems200ResponseDataInner(self):
        """Test ListProcessRunWorkItems200ResponseDataInner"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()