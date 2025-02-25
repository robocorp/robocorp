# coding: utf-8

"""
    Robocorp Control Room API

    Robocorp Control Room API  # noqa: E501

    OpenAPI spec version: 1.0
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""

from __future__ import absolute_import

import unittest

import swagger_client
from swagger_client.api.work_item_api import WorkItemApi  # noqa: E501
from swagger_client.rest import ApiException


class TestWorkItemApi(unittest.TestCase):
    """WorkItemApi unit test stubs"""

    def setUp(self):
        self.api = WorkItemApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_create_work_item(self):
        """Test case for create_work_item

        Create work item  # noqa: E501
        """
        pass

    def test_create_work_item_file(self):
        """Test case for create_work_item_file

        Create work item file  # noqa: E501
        """
        pass

    def test_get_work_item(self):
        """Test case for get_work_item

        Get work item  # noqa: E501
        """
        pass

    def test_list_process_run_work_items(self):
        """Test case for list_process_run_work_items

        List work items of a process run  # noqa: E501
        """
        pass

    def test_list_process_work_items(self):
        """Test case for list_process_work_items

        List work items of process  # noqa: E501
        """
        pass

    def test_run_work_item_batch_operation(self):
        """Test case for run_work_item_batch_operation

        Retry, delete or mark work items as done  # noqa: E501
        """
        pass

    def test_update_work_item_payload(self):
        """Test case for update_work_item_payload

        Update work item payload  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
