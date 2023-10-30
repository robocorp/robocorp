# robocorp.workspace.ProcessApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_processes**](ProcessApi.md#list_processes) | **GET** /workspaces/{workspace_id}/processes | List processes


# **list_processes**
> ListProcesses200Response list_processes(workspace_id, limit=limit)

List processes

Returns a list of all processes linked to the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.list_processes200_response import ListProcesses200Response
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
    api_instance = robocorp.workspace.ProcessApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    limit = 3.4 # float | Limit for paginated response (optional)

    try:
        # List processes
        api_response = api_instance.list_processes(workspace_id, limit=limit)
        print("The response of ProcessApi->list_processes:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProcessApi->list_processes: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**ListProcesses200Response**](ListProcesses200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Processes |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
