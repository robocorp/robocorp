# swagger_client.AssistantApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_assistant**](AssistantApi.md#create_assistant) | **POST** /workspaces/{workspace_id}/assistants | Create assistant
[**get_assistant**](AssistantApi.md#get_assistant) | **GET** /workspaces/{workspace_id}/assistants/{assistant_id} | Get assistant
[**get_assistant_run**](AssistantApi.md#get_assistant_run) | **GET** /workspaces/{workspace_id}/assistant-runs/{assistant_run_id} | Get assistant run
[**list_assistant_assistant_runs**](AssistantApi.md#list_assistant_assistant_runs) | **GET** /workspaces/{workspace_id}/assistants/{assistant_id}/assistant-runs | List assistant runs for an assistant
[**list_assistants**](AssistantApi.md#list_assistants) | **GET** /workspaces/{workspace_id}/assistants | List assistants
[**list_workspace_assistant_runs**](AssistantApi.md#list_workspace_assistant_runs) | **GET** /workspaces/{workspace_id}/assistant-runs | List assistant runs for workspace

# **create_assistant**
> InlineResponse20024 create_assistant(body, workspace_id)

Create assistant

Creates a new assistant with the given name and for the specified task inside a task package.

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
api_instance = swagger_client.AssistantApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkspaceIdAssistantsBody() # WorkspaceIdAssistantsBody | 
workspace_id = 'workspace_id_example' # str | Workspace ID

try:
    # Create assistant
    api_response = api_instance.create_assistant(body, workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AssistantApi->create_assistant: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkspaceIdAssistantsBody**](WorkspaceIdAssistantsBody.md)|  | 
 **workspace_id** | **str**| Workspace ID | 

### Return type

[**InlineResponse20024**](InlineResponse20024.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_assistant**
> InlineResponse20025 get_assistant(workspace_id, assistant_id)

Get assistant

Returns an assistant

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
api_instance = swagger_client.AssistantApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
assistant_id = 'assistant_id_example' # str | Assistant ID

try:
    # Get assistant
    api_response = api_instance.get_assistant(workspace_id, assistant_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AssistantApi->get_assistant: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **assistant_id** | **str**| Assistant ID | 

### Return type

[**InlineResponse20025**](InlineResponse20025.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_assistant_run**
> AssistantRunResource get_assistant_run(workspace_id, assistant_run_id)

Get assistant run

Returns an assistant run for the requested assistant.

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
api_instance = swagger_client.AssistantApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
assistant_run_id = 'assistant_run_id_example' # str | Assistant Run ID

try:
    # Get assistant run
    api_response = api_instance.get_assistant_run(workspace_id, assistant_run_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AssistantApi->get_assistant_run: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **assistant_run_id** | **str**| Assistant Run ID | 

### Return type

[**AssistantRunResource**](AssistantRunResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_assistant_assistant_runs**
> InlineResponse20026 list_assistant_assistant_runs(workspace_id, assistant_id, limit=limit)

List assistant runs for an assistant

Returns a paginated list of assistant runs for the assistant.

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
api_instance = swagger_client.AssistantApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
assistant_id = 'assistant_id_example' # str | Assistant ID
limit = 1.2 # float | Limit for paginated response (optional)

try:
    # List assistant runs for an assistant
    api_response = api_instance.list_assistant_assistant_runs(workspace_id, assistant_id, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AssistantApi->list_assistant_assistant_runs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **assistant_id** | **str**| Assistant ID | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**InlineResponse20026**](InlineResponse20026.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_assistants**
> InlineResponse20023 list_assistants(workspace_id)

List assistants

Returns a paginated list of assistants for the workspace.

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
api_instance = swagger_client.AssistantApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID

try:
    # List assistants
    api_response = api_instance.list_assistants(workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AssistantApi->list_assistants: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 

### Return type

[**InlineResponse20023**](InlineResponse20023.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_workspace_assistant_runs**
> InlineResponse20026 list_workspace_assistant_runs(workspace_id, limit=limit)

List assistant runs for workspace

Returns a paginated list of assistant runs for the workspace.

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
api_instance = swagger_client.AssistantApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
limit = 1.2 # float | Limit for paginated response (optional)

try:
    # List assistant runs for workspace
    api_response = api_instance.list_workspace_assistant_runs(workspace_id, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AssistantApi->list_workspace_assistant_runs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**InlineResponse20026**](InlineResponse20026.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

