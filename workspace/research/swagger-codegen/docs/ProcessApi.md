# swagger_client.ProcessApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_processes**](ProcessApi.md#list_processes) | **GET** /workspaces/{workspace_id}/processes | List processes

# **list_processes**
> InlineResponse2008 list_processes(workspace_id)

List processes

Returns a list of all processes linked to the requested workspace.

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
api_instance = swagger_client.ProcessApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID

try:
    # List processes
    api_response = api_instance.list_processes(workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProcessApi->list_processes: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 

### Return type

[**InlineResponse2008**](InlineResponse2008.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

