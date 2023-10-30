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
from swagger_client.api.assistant_api import AssistantApi  # noqa: E501
from swagger_client.rest import ApiException


class TestAssistantApi(unittest.TestCase):
    """AssistantApi unit test stubs"""

    def setUp(self):
        self.api = AssistantApi()  # noqa: E501

    def tearDown(self):
        pass

    def test_create_assistant(self):
        """Test case for create_assistant

        Create assistant  # noqa: E501
        """
        pass

    def test_get_assistant(self):
        """Test case for get_assistant

        Get assistant  # noqa: E501
        """
        pass

    def test_get_assistant_run(self):
        """Test case for get_assistant_run

        Get assistant run  # noqa: E501
        """
        pass

    def test_list_assistant_assistant_runs(self):
        """Test case for list_assistant_assistant_runs

        List assistant runs for an assistant  # noqa: E501
        """
        pass

    def test_list_assistants(self):
        """Test case for list_assistants

        List assistants  # noqa: E501
        """
        pass

    def test_list_workspace_assistant_runs(self):
        """Test case for list_workspace_assistant_runs

        List assistant runs for workspace  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()