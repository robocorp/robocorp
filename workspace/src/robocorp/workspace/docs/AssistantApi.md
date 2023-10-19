# workspace.AssistantApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_assistant**](AssistantApi.md#create_assistant) | **POST** /workspaces/{workspace_id}/assistants | Create assistant
[**get_assistant**](AssistantApi.md#get_assistant) | **GET** /workspaces/{workspace_id}/assistants/{assistant_id} | Get assistant
[**get_assistant_run**](AssistantApi.md#get_assistant_run) | **GET** /workspaces/{workspace_id}/assistant-runs/{assistant_run_id} | Get assistant run
[**list_assistant_assistant_runs**](AssistantApi.md#list_assistant_assistant_runs) | **GET** /workspaces/{workspace_id}/assistants/{assistant_id}/assistant-runs | List assistant runs for an assistant
[**list_assistants**](AssistantApi.md#list_assistants) | **GET** /workspaces/{workspace_id}/assistants | List assistants
[**list_workspace_assistant_runs**](AssistantApi.md#list_workspace_assistant_runs) | **GET** /workspaces/{workspace_id}/assistant-runs | List assistant runs for workspace


# **create_assistant**
> ListAssets200ResponseDataInner create_assistant(workspace_id, create_assistant_request)

Create assistant

Creates a new assistant with the given name and for the specified task inside a task package.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.create_assistant_request import CreateAssistantRequest
from workspace.models.list_assets200_response_data_inner import ListAssets200ResponseDataInner
from workspace.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = workspace.Configuration(
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
with workspace.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace.AssistantApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    create_assistant_request = workspace.CreateAssistantRequest() # CreateAssistantRequest | 

    try:
        # Create assistant
        api_response = api_instance.create_assistant(workspace_id, create_assistant_request)
        print("The response of AssistantApi->create_assistant:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssistantApi->create_assistant: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **create_assistant_request** | [**CreateAssistantRequest**](CreateAssistantRequest.md)|  | 

### Return type

[**ListAssets200ResponseDataInner**](ListAssets200ResponseDataInner.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Assistant |  -  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**409** | Conflict |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_assistant**
> GetAssistant200Response get_assistant(workspace_id, assistant_id)

Get assistant

Returns an assistant

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.get_assistant200_response import GetAssistant200Response
from workspace.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = workspace.Configuration(
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
with workspace.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace.AssistantApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    assistant_id = 'assistant_id_example' # str | Assistant ID

    try:
        # Get assistant
        api_response = api_instance.get_assistant(workspace_id, assistant_id)
        print("The response of AssistantApi->get_assistant:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssistantApi->get_assistant: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **assistant_id** | **str**| Assistant ID | 

### Return type

[**GetAssistant200Response**](GetAssistant200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Assistant |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_assistant_run**
> AssistantRunResource get_assistant_run(workspace_id, assistant_run_id)

Get assistant run

Returns an assistant run for the requested assistant.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.assistant_run_resource import AssistantRunResource
from workspace.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = workspace.Configuration(
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
with workspace.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace.AssistantApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    assistant_run_id = 'assistant_run_id_example' # str | Assistant Run ID

    try:
        # Get assistant run
        api_response = api_instance.get_assistant_run(workspace_id, assistant_run_id)
        print("The response of AssistantApi->get_assistant_run:\n")
        pprint(api_response)
    except Exception as e:
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

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Assistant Run |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_assistant_assistant_runs**
> ListAssistantAssistantRuns200Response list_assistant_assistant_runs(workspace_id, assistant_id, limit=limit)

List assistant runs for an assistant

Returns a paginated list of assistant runs for the assistant.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.list_assistant_assistant_runs200_response import ListAssistantAssistantRuns200Response
from workspace.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = workspace.Configuration(
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
with workspace.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace.AssistantApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    assistant_id = 'assistant_id_example' # str | Assistant ID
    limit = 3.4 # float | Limit for paginated response (optional)

    try:
        # List assistant runs for an assistant
        api_response = api_instance.list_assistant_assistant_runs(workspace_id, assistant_id, limit=limit)
        print("The response of AssistantApi->list_assistant_assistant_runs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssistantApi->list_assistant_assistant_runs: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **assistant_id** | **str**| Assistant ID | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**ListAssistantAssistantRuns200Response**](ListAssistantAssistantRuns200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Assistant Runs |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_assistants**
> ListAssistants200Response list_assistants(workspace_id, limit=limit)

List assistants

Returns a paginated list of assistants for the workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.list_assistants200_response import ListAssistants200Response
from workspace.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = workspace.Configuration(
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
with workspace.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace.AssistantApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    limit = 3.4 # float | Limit for paginated response (optional)

    try:
        # List assistants
        api_response = api_instance.list_assistants(workspace_id, limit=limit)
        print("The response of AssistantApi->list_assistants:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssistantApi->list_assistants: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**ListAssistants200Response**](ListAssistants200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Assistants |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_workspace_assistant_runs**
> ListAssistantAssistantRuns200Response list_workspace_assistant_runs(workspace_id, limit=limit)

List assistant runs for workspace

Returns a paginated list of assistant runs for the workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.list_assistant_assistant_runs200_response import ListAssistantAssistantRuns200Response
from workspace.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = workspace.Configuration(
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
with workspace.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = workspace.AssistantApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    limit = 3.4 # float | Limit for paginated response (optional)

    try:
        # List assistant runs for workspace
        api_response = api_instance.list_workspace_assistant_runs(workspace_id, limit=limit)
        print("The response of AssistantApi->list_workspace_assistant_runs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssistantApi->list_workspace_assistant_runs: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**ListAssistantAssistantRuns200Response**](ListAssistantAssistantRuns200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Assistant Runs |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

