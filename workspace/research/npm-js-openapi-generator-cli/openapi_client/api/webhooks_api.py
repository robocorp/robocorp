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
from openapi_client.models.list_webhooks200_response import ListWebhooks200Response
from openapi_client.models.process_webhook_payload import ProcessWebhookPayload
from openapi_client.models.webhook_resource import WebhookResource

from openapi_client.api_client import ApiClient
from openapi_client.api_response import ApiResponse
from openapi_client.exceptions import (  # noqa: F401
    ApiTypeError,
    ApiValueError
)


class WebhooksApi:
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None) -> None:
        if api_client is None:
            api_client = ApiClient.get_default()
        self.api_client = api_client

    @validate_arguments
    def create_webhook(self, workspace_id : Annotated[StrictStr, Field(..., description="The ID of the workspace")], process_webhook_payload : ProcessWebhookPayload, **kwargs) -> WebhookResource:  # noqa: E501
        """Create Process webhook  # noqa: E501

        Creates a process webhook for the requested workspace.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.create_webhook(workspace_id, process_webhook_payload, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The ID of the workspace (required)
        :type workspace_id: str
        :param process_webhook_payload: (required)
        :type process_webhook_payload: ProcessWebhookPayload
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: WebhookResource
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the create_webhook_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.create_webhook_with_http_info(workspace_id, process_webhook_payload, **kwargs)  # noqa: E501

    @validate_arguments
    def create_webhook_with_http_info(self, workspace_id : Annotated[StrictStr, Field(..., description="The ID of the workspace")], process_webhook_payload : ProcessWebhookPayload, **kwargs) -> ApiResponse:  # noqa: E501
        """Create Process webhook  # noqa: E501

        Creates a process webhook for the requested workspace.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.create_webhook_with_http_info(workspace_id, process_webhook_payload, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The ID of the workspace (required)
        :type workspace_id: str
        :param process_webhook_payload: (required)
        :type process_webhook_payload: ProcessWebhookPayload
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
        :rtype: tuple(WebhookResource, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'workspace_id',
            'process_webhook_payload'
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
                    " to method create_webhook" % _key
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
        if _params['process_webhook_payload'] is not None:
            _body_params = _params['process_webhook_payload']

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
            '200': "WebhookResource",
            '400': "GenericErrorResponse",
            '403': "GenericErrorResponse",
        }

        return self.api_client.call_api(
            '/workspaces/{workspace_id}/webhooks', 'POST',
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
    def delete_webhook(self, workspace_id : Annotated[StrictStr, Field(..., description="The ID of the workspace")], webhook_id : Annotated[StrictStr, Field(..., description="The ID of the webhook")], **kwargs) -> DeleteWorker200Response:  # noqa: E501
        """Delete webhook  # noqa: E501

        Deletes the requested webhook. This action is irreversible!  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.delete_webhook(workspace_id, webhook_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The ID of the workspace (required)
        :type workspace_id: str
        :param webhook_id: The ID of the webhook (required)
        :type webhook_id: str
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
            message = "Error! Please call the delete_webhook_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.delete_webhook_with_http_info(workspace_id, webhook_id, **kwargs)  # noqa: E501

    @validate_arguments
    def delete_webhook_with_http_info(self, workspace_id : Annotated[StrictStr, Field(..., description="The ID of the workspace")], webhook_id : Annotated[StrictStr, Field(..., description="The ID of the webhook")], **kwargs) -> ApiResponse:  # noqa: E501
        """Delete webhook  # noqa: E501

        Deletes the requested webhook. This action is irreversible!  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.delete_webhook_with_http_info(workspace_id, webhook_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The ID of the workspace (required)
        :type workspace_id: str
        :param webhook_id: The ID of the webhook (required)
        :type webhook_id: str
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
            'webhook_id'
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
                    " to method delete_webhook" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}
        if _params['workspace_id']:
            _path_params['workspace_id'] = _params['workspace_id']

        if _params['webhook_id']:
            _path_params['webhook_id'] = _params['webhook_id']


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
            '/workspaces/{workspace_id}/webhooks/{webhook_id}', 'DELETE',
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
    def get_webhook(self, workspace_id : Annotated[StrictStr, Field(..., description="The ID of the workspace")], webhook_id : Annotated[StrictStr, Field(..., description="The ID of the webhook")], **kwargs) -> WebhookResource:  # noqa: E501
        """Get Webhook  # noqa: E501

        Returns a webhook for the requested workspace.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_webhook(workspace_id, webhook_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The ID of the workspace (required)
        :type workspace_id: str
        :param webhook_id: The ID of the webhook (required)
        :type webhook_id: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: WebhookResource
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the get_webhook_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.get_webhook_with_http_info(workspace_id, webhook_id, **kwargs)  # noqa: E501

    @validate_arguments
    def get_webhook_with_http_info(self, workspace_id : Annotated[StrictStr, Field(..., description="The ID of the workspace")], webhook_id : Annotated[StrictStr, Field(..., description="The ID of the webhook")], **kwargs) -> ApiResponse:  # noqa: E501
        """Get Webhook  # noqa: E501

        Returns a webhook for the requested workspace.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.get_webhook_with_http_info(workspace_id, webhook_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The ID of the workspace (required)
        :type workspace_id: str
        :param webhook_id: The ID of the webhook (required)
        :type webhook_id: str
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
        :rtype: tuple(WebhookResource, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'workspace_id',
            'webhook_id'
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
                    " to method get_webhook" % _key
                )
            _params[_key] = _val
        del _params['kwargs']

        _collection_formats = {}

        # process the path parameters
        _path_params = {}
        if _params['workspace_id']:
            _path_params['workspace_id'] = _params['workspace_id']

        if _params['webhook_id']:
            _path_params['webhook_id'] = _params['webhook_id']


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
            '200': "WebhookResource",
            '403': "GenericErrorResponse",
            '404': "GenericErrorResponse",
        }

        return self.api_client.call_api(
            '/workspaces/{workspace_id}/webhooks/{webhook_id}', 'GET',
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
    def list_webhooks(self, workspace_id : Annotated[StrictStr, Field(..., description="The ID of the workspace")], **kwargs) -> ListWebhooks200Response:  # noqa: E501
        """List Webhooks  # noqa: E501

        Retrieves a list of all webhooks for the requested workspace.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.list_webhooks(workspace_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The ID of the workspace (required)
        :type workspace_id: str
        :param async_req: Whether to execute the request asynchronously.
        :type async_req: bool, optional
        :param _request_timeout: timeout setting for this request.
               If one number provided, it will be total request
               timeout. It can also be a pair (tuple) of
               (connection, read) timeouts.
        :return: Returns the result object.
                 If the method is called asynchronously,
                 returns the request thread.
        :rtype: ListWebhooks200Response
        """
        kwargs['_return_http_data_only'] = True
        if '_preload_content' in kwargs:
            message = "Error! Please call the list_webhooks_with_http_info method with `_preload_content` instead and obtain raw data from ApiResponse.raw_data"  # noqa: E501
            raise ValueError(message)
        return self.list_webhooks_with_http_info(workspace_id, **kwargs)  # noqa: E501

    @validate_arguments
    def list_webhooks_with_http_info(self, workspace_id : Annotated[StrictStr, Field(..., description="The ID of the workspace")], **kwargs) -> ApiResponse:  # noqa: E501
        """List Webhooks  # noqa: E501

        Retrieves a list of all webhooks for the requested workspace.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.list_webhooks_with_http_info(workspace_id, async_req=True)
        >>> result = thread.get()

        :param workspace_id: The ID of the workspace (required)
        :type workspace_id: str
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
        :rtype: tuple(ListWebhooks200Response, status_code(int), headers(HTTPHeaderDict))
        """

        _params = locals()

        _all_params = [
            'workspace_id'
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
                    " to method list_webhooks" % _key
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
        # set the HTTP header `Accept`
        _header_params['Accept'] = self.api_client.select_header_accept(
            ['application/json'])  # noqa: E501

        # authentication setting
        _auth_settings = ['API Key with permissions']  # noqa: E501

        _response_types_map = {
            '200': "ListWebhooks200Response",
            '403': "GenericErrorResponse",
        }

        return self.api_client.call_api(
            '/workspaces/{workspace_id}/webhooks', 'GET',
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
