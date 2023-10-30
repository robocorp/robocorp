# robocorp.workspace.WorkspaceApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_workspace**](WorkspaceApi.md#get_workspace) | **GET** /workspaces/{workspace_id} | Get workspace


# **get_workspace**
> WorkspaceResource get_workspace(workspace_id)

Get workspace

Returns the workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.workspace_resource import WorkspaceResource
from robocorp.workspace.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = robocorp.workspace.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: API Key with permissions
configuration.api_key['API Key with permissions'] = os.environ["API_KEY"]

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['API Key with permissions'] = 'Bearer'

# Enter a context with an instance of the API client
with robocorp.workspace.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = robocorp.workspace.WorkspaceApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace.

    try:
        # Get workspace
        api_response = api_instance.get_workspace(workspace_id)
        print("The response of WorkspaceApi->get_workspace:\n")
        pprint(api_response)
    except Exception as e:
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

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Workspace |  * Access-Control-Allow-Origin -  <br>  |
**401** | Unauthorized |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

