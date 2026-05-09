# swagger_client.WorkspaceApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_workspace**](WorkspaceApi.md#get_workspace) | **GET** /workspaces/{workspace_id} | Get workspace

# **get_workspace**
> WorkspaceResource get_workspace(workspace_id)

Get workspace

Returns the workspace.

### Example
```python
from __future__ import print_function
import time
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Configure API key authorization: API Key with permissions
configuration = swagger_client.Configuration()
configuration.api_key['Authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = swagger_client.WorkspaceApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace.

try:
    # Get workspace
    api_response = api_instance.get_workspace(workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkspaceApi->get_workspace: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace. | 

### Return type

[**WorkspaceResource**](WorkspaceResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

