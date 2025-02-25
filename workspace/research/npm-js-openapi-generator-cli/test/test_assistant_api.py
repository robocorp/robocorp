# coding: utf-8

"""
    Robocorp Control Room API

    Robocorp Control Room API

    The version of the OpenAPI document: 1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from openapi_client.api.assistant_api import AssistantApi  # noqa: E501


class TestAssistantApi(unittest.TestCase):
    """AssistantApi unit test stubs"""

    def setUp(self) -> None:
        self.api = AssistantApi()  # noqa: E501

    def tearDown(self) -> None:
        pass

    def test_create_assistant(self) -> None:
        """Test case for create_assistant

        Create assistant  # noqa: E501
        """
        pass

    def test_get_assistant(self) -> None:
        """Test case for get_assistant

        Get assistant  # noqa: E501
        """
        pass

    def test_get_assistant_run(self) -> None:
        """Test case for get_assistant_run

        Get assistant run  # noqa: E501
        """
        pass

    def test_list_assistant_assistant_runs(self) -> None:
        """Test case for list_assistant_assistant_runs

        List assistant runs for an assistant  # noqa: E501
        """
        pass

    def test_list_assistants(self) -> None:
        """Test case for list_assistants

        List assistants  # noqa: E501
        """
        pass

    def test_list_workspace_assistant_runs(self) -> None:
        """Test case for list_workspace_assistant_runs

        List assistant runs for workspace  # noqa: E501
        """
        pass


if __name__ == '__main__':
    unittest.main()
