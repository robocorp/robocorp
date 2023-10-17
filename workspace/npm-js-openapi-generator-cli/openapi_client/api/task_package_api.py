# coding: utf-8

"""
    Robocorp Control Room API

    Robocorp Control Room API

    The version of the OpenAPI document: 1.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import re  # noqa: F401
import io
import warnings

from pydantic import validate_arguments, ValidationError

from typing_extensions import Annotated
from pydantic import Field, StrictStr

from openapi_client.models.delete_worker200_response import DeleteWorker200Response
from openapi_client.models.task_package_download_link import TaskPackageDownloadLink
from openapi_client.models.task_package_resource import TaskPackageResource
from openapi_client.models.task_package_upload_link import TaskPackageUploadLink
from openapi_client.models.update_worker_request import UpdateWorkerRequest

from openapi_client.api_client import ApiClient
from openapi_client.api_response import ApiResponse
from openapi_client.exceptions import (  # noqa: F401
    ApiTypeError,
    ApiValueError
)


class TaskPackageApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client

    @validate_arguments
    def create_task_package(self, workspace_id : Annotated[StrictStr, Field(..., description="The id of the workspace in which to create the task package")], update_worker_request : Annotated[UpdateWorkerRequest, Field(..., description="The name of the task package to create")], **kwargs) -> TaskPackageResource:  # noqa: E501
        """Create new task package  # noqa: E501

        Creates a new task package with the given name in the requested workspace.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.create_task_package(workspace_id, update_worker_request, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The id of the workspace in which to create the task package (required)
        :type workspace_id: str
        :param update_worker_request: The name of the task package to create (required)
        :type update_worker_request: UpdateWorkerRequest
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: TaskPackageResource
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the create_task_package_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.create_task_package_with_http_info(workspace_id, update_worker_request, **kwargs)  # noqa: E501

    @validate_arguments
    def create_task_package_with_http_info(self, workspace_id : Annotated[StrictStr, Field(..., description="The id of the workspace in which to create the task package")], update_worker_request : Annotated[UpdateWorkerRequest, Field(..., description="The name of the task package to create")], **kwargs) -> ApiResponse:  # noqa: E501
        """Create new task package  # noqa: E501

        Creates a new task package with the given name in the requested workspace.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.create_task_package_with_http_info(workspace_id, update_worker_request, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The id of the workspace in which to create the task package (required)
        :type workspace_id: str
        :param update_worker_request: The name of the task package to create (required)
        :type update_worker_request: UpdateWorkerRequest
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(TaskPackageResource, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'workspace_id',
            'update_worker_request'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method create_task_package" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}
        if _params['workspace_id']:
            _path_params['workspace_id'] = _params['workspace_id']


        # process the query parameters
        _query_params = []
        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        if _params['update_worker_request'] is not None:
            _body_params = _params['update_worker_request']

        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # set the HTTP header `Content-Type`
        _content_types_list = _params.get('_content_type',
            self.api_client.select_header_content_type(
                ['application/json']))
        if _content_types_list:
                _header_params['Content-Type'] = _content_types_list

        # authentication setting
        _auth_settings = ['API Key with permissions']  # noqa: E501

        _response_types_map = {
            '200': "TaskPackageResource",
            '400': "GenericErrorResponse",
            '403': "GenericErrorResponse",
        }

        return self.api_client.call_api(
            '/workspaces/{workspace_id}/task-packages', 'POST',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))

    @validate_arguments
    def delete_task_package(self, workspace_id : Annotated[StrictStr, Field(..., description="The id of the workspace on which the task package resides.")], task_package_id : Annotated[StrictStr, Field(..., description="The id of the task package to delete.")], **kwargs) -> DeleteWorker200Response:  # noqa: E501
        """Delete task package  # noqa: E501

        Deletes a specific task package. This action is irreversible!  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.delete_task_package(workspace_id, task_package_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The id of the workspace on which the task package resides. (required)
        :type workspace_id: str
        :param task_package_id: The id of the task package to delete. (required)
        :type task_package_id: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: DeleteWorker200Response
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the delete_task_package_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.delete_task_package_with_http_info(workspace_id, task_package_id, **kwargs)  # noqa: E501

    @validate_arguments
    def delete_task_package_with_http_info(self, workspace_id : Annotated[StrictStr, Field(..., description="The id of the workspace on which the task package resides.")], task_package_id : Annotated[StrictStr, Field(..., description="The id of the task package to delete.")], **kwargs) -> ApiResponse:  # noqa: E501
        """Delete task package  # noqa: E501

        Deletes a specific task package. This action is irreversible!  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.delete_task_package_with_http_info(workspace_id, task_package_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The id of the workspace on which the task package resides. (required)
        :type workspace_id: str
        :param task_package_id: The id of the task package to delete. (required)
        :type task_package_id: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(DeleteWorker200Response, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'workspace_id',
            'task_package_id'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method delete_task_package" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}
        if _params['workspace_id']:
            _path_params['workspace_id'] = _params['workspace_id']

        if _params['task_package_id']:
            _path_params['task_package_id'] = _params['task_package_id']


        # process the query parameters
        _query_params = []
        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # authentication setting
        _auth_settings = ['API Key with permissions']  # noqa: E501

        _response_types_map = {
            '200': "DeleteWorker200Response",
            '403': "GenericErrorResponse",
        }

        return self.api_client.call_api(
            '/workspaces/{workspace_id}/task-packages/{task_package_id}', 'DELETE',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))

    @validate_arguments
    def get_task_package_download_link(self, workspace_id : Annotated[StrictStr, Field(..., description="The id of the workspace in which the task package resides")], task_package_id : Annotated[StrictStr, Field(..., description="The id of the task package to get the download link for")], **kwargs) -> TaskPackageDownloadLink:  # noqa: E501
        """Get task package download link  # noqa: E501

        Returns a URL to download the task package bundle.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_task_package_download_link(workspace_id, task_package_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The id of the workspace in which the task package resides (required)
        :type workspace_id: str
        :param task_package_id: The id of the task package to get the download link for (required)
        :type task_package_id: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: TaskPackageDownloadLink
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the get_task_package_download_link_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.get_task_package_download_link_with_http_info(workspace_id, task_package_id, **kwargs)  # noqa: E501

    @validate_arguments
    def get_task_package_download_link_with_http_info(self, workspace_id : Annotated[StrictStr, Field(..., description="The id of the workspace in which the task package resides")], task_package_id : Annotated[StrictStr, Field(..., description="The id of the task package to get the download link for")], **kwargs) -> ApiResponse:  # noqa: E501
        """Get task package download link  # noqa: E501

        Returns a URL to download the task package bundle.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_task_package_download_link_with_http_info(workspace_id, task_package_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The id of the workspace in which the task package resides (required)
        :type workspace_id: str
        :param task_package_id: The id of the task package to get the download link for (required)
        :type task_package_id: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(TaskPackageDownloadLink, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'workspace_id',
            'task_package_id'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_task_package_download_link" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}
        if _params['workspace_id']:
            _path_params['workspace_id'] = _params['workspace_id']

        if _params['task_package_id']:
            _path_params['task_package_id'] = _params['task_package_id']


        # process the query parameters
        _query_params = []
        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # authentication setting
        _auth_settings = ['API Key with permissions']  # noqa: E501

        _response_types_map = {
            '200': "TaskPackageDownloadLink",
            '403': "GenericErrorResponse",
        }

        return self.api_client.call_api(
            '/workspaces/{workspace_id}/task-packages/{task_package_id}/download', 'GET',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))

    @validate_arguments
    def get_task_package_upload_link(self, workspace_id : Annotated[StrictStr, Field(..., description="The id of the workspace in which the task package resides")], task_package_id : Annotated[StrictStr, Field(..., description="The id of the task package to get the upload link for")], **kwargs) -> TaskPackageUploadLink:  # noqa: E501
        """Get task package upload link  # noqa: E501

        Returns a URL + form data payload for uploading the task package bundle.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_task_package_upload_link(workspace_id, task_package_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The id of the workspace in which the task package resides (required)
        :type workspace_id: str
        :param task_package_id: The id of the task package to get the upload link for (required)
        :type task_package_id: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: TaskPackageUploadLink
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the get_task_package_upload_link_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.get_task_package_upload_link_with_http_info(workspace_id, task_package_id, **kwargs)  # noqa: E501

    @validate_arguments
    def get_task_package_upload_link_with_http_info(self, workspace_id : Annotated[StrictStr, Field(..., description="The id of the workspace in which the task package resides")], task_package_id : Annotated[StrictStr, Field(..., description="The id of the task package to get the upload link for")], **kwargs) -> ApiResponse:  # noqa: E501
        """Get task package upload link  # noqa: E501

        Returns a URL + form data payload for uploading the task package bundle.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_task_package_upload_link_with_http_info(workspace_id, task_package_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The id of the workspace in which the task package resides (required)
        :type workspace_id: str
        :param task_package_id: The id of the task package to get the upload link for (required)
        :type task_package_id: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _preload_content: if False, the ApiResponse.data will
                                 be set to none and raw_data will store the
                                 HTTP response body without reading/decoding.
                                 Default is True.
        :type _preload_content: bool, optional
        :param _return_http_data_only: response data instead of ApiResponse
                                       object with status code, headers, etc
        :type _return_http_data_only: bool, optional
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        :param _request_auth: set to override the auth_settings for an a single
                              request; this effectively ignores the authentication
                              in the spec for a single request.
        :type _request_auth: dict, optional
        :type _content_type: string, optional: force content-type for the request
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: tuple(TaskPackageUploadLink, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'workspace_id',
            'task_package_id'
        ]
        _all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout',
                '_request_auth',
                '_content_type',
                '_headers'
            ]
        )

        # validate the arguments
        for _key, _val in _params['kwargs'].items():
            if _key not in _all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_task_package_upload_link" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}
        if _params['workspace_id']:
            _path_params['workspace_id'] = _params['workspace_id']

        if _params['task_package_id']:
            _path_params['task_package_id'] = _params['task_package_id']


        # process the query parameters
        _query_params = []
        # process the header parameters
        _header_params = dict(_params.get('_headers', {}))
        # process the form parameters
        _form_params = []
        _files = {}
        # process the body parameter
        _body_params = None
        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # authentication setting
        _auth_settings = ['API Key with permissions']  # noqa: E501

        _response_types_map = {
            '200': "TaskPackageUploadLink",
            '403': "GenericErrorResponse",
        }

        return self.api_client.call_api(
            '/workspaces/{workspace_id}/task-packages/{task_package_id}/upload', 'GET',
            _path_params,
            _query_params,
            _header_params,
            body=_body_params,
            post_params=_form_params,
            files=_files,
            response_types_map=_response_types_map,
            auth_settings=_auth_settings,
            async_req=_params.get('async_req'),
            _return_http_data_only=_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=_params.get('_preload_content', True),
            _request_timeout=_params.get('_request_timeout'),
            collection_formats=_collection_formats,
            _request_auth=_params.get('_request_auth'))
