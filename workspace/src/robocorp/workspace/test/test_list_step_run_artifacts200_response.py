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

from workspace.models.list_step_run_artifacts200_response import ListStepRunArtifacts200Response  # noqa: E501

class TestListStepRunArtifacts200Response(unittest.TestCase):
    """ListStepRunArtifacts200Response unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> ListStepRunArtifacts200Response:
        """Test ListStepRunArtifacts200Response
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `ListStepRunArtifacts200Response`
        """
        model = ListStepRunArtifacts200Response()  # noqa: E501
        if include_optional:
            return ListStepRunArtifacts200Response(
                next = None,
                has_more = None,
                data = [
                    workspace.models.list_step_run_artifacts_200_response_data_inner.listStepRunArtifacts_200_response_data_inner(
                        id = '', 
                        name = '', 
                        size = 1.337, )
                    ]
            )
        else:
            return ListStepRunArtifacts200Response(
                next = None,
                has_more = None,
                data = [
                    workspace.models.list_step_run_artifacts_200_response_data_inner.listStepRunArtifacts_200_response_data_inner(
                        id = '', 
                        name = '', 
                        size = 1.337, )
                    ],
        )
        """

    def testListStepRunArtifacts200Response(self):
        """Test ListStepRunArtifacts200Response"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()