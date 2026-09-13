# robocorp.workspace.ProcessRunApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_process_run**](ProcessRunApi.md#delete_process_run) | **DELETE** /workspaces/{workspace_id}/process-runs/{process_run_id} | Delete process run
[**get_process_run**](ProcessRunApi.md#get_process_run) | **GET** /workspaces/{workspace_id}/process-runs/{process_run_id} | Get process run
[**list_process_run_outputs**](ProcessRunApi.md#list_process_run_outputs) | **GET** /workspaces/{workspace_id}/outputs | List process run outputs
[**list_process_runs**](ProcessRunApi.md#list_process_runs) | **GET** /workspaces/{workspace_id}/process-runs | List process runs
[**start_process_run**](ProcessRunApi.md#start_process_run) | **POST** /workspaces/{workspace_id}/processes/{process_id}/process-runs | Start process run
[**start_process_run_qs_auth**](ProcessRunApi.md#start_process_run_qs_auth) | **POST** /workspaces/{workspace_id}/processes/{process_id}/process-runs-integrations | Start process run (for integrations)
[**stop_process_run**](ProcessRunApi.md#stop_process_run) | **POST** /workspaces/{workspace_id}/process-runs/{process_run_id}/stop | Stop process run


# **delete_process_run**
> DeleteWorker200Response delete_process_run(workspace_id, process_run_id)

Delete process run

Deletes a process run. This action is irreversible!

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.delete_worker200_response import DeleteWorker200Response
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
    api_instance = robocorp.workspace.ProcessRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the robot resides.
    process_run_id = 'process_run_id_example' # str | The id of the process run to delete.

    try:
        # Delete process run
        api_response = api_instance.delete_process_run(workspace_id, process_run_id)
        print("The response of ProcessRunApi->delete_process_run:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProcessRunApi->delete_process_run: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the robot resides. | 
 **process_run_id** | **str**| The id of the process run to delete. | 

### Return type

[**DeleteWorker200Response**](DeleteWorker200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Deleted Process Run |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |
**409** | Conflict |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_process_run**
> ProcessRunResource get_process_run(workspace_id, process_run_id)

Get process run

Returns a process run

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.process_run_resource import ProcessRunResource
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
    api_instance = robocorp.workspace.ProcessRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    process_run_id = 'process_run_id_example' # str | ID of the process run

    try:
        # Get process run
        api_response = api_instance.get_process_run(workspace_id, process_run_id)
        print("The response of ProcessRunApi->get_process_run:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProcessRunApi->get_process_run: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **process_run_id** | **str**| ID of the process run | 

### Return type

[**ProcessRunResource**](ProcessRunResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Process Run |  -  |
**403** | Forbidden |  -  |
**404** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_process_run_outputs**
> ListProcessRunOutputs200Response list_process_run_outputs(workspace_id, process_run_id, limit=limit)

List process run outputs

Returns a list of process run outputs.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.list_process_run_outputs200_response import ListProcessRunOutputs200Response
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
    api_instance = robocorp.workspace.ProcessRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    process_run_id = 'process_run_id_example' # str | Process Run ID
    limit = 3.4 # float | Limit for paginated response (optional)

    try:
        # List process run outputs
        api_response = api_instance.list_process_run_outputs(workspace_id, process_run_id, limit=limit)
        print("The response of ProcessRunApi->list_process_run_outputs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProcessRunApi->list_process_run_outputs: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **process_run_id** | **str**| Process Run ID | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**ListProcessRunOutputs200Response**](ListProcessRunOutputs200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Process Run Outputs |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_process_runs**
> ListProcessRuns200Response list_process_runs(workspace_id, process_id=process_id, state=state, limit=limit)

List process runs

Returns a paginated list of process runs. If a process id is specified in the query parameters, the response will only contain process runs from that process. If not, the response will contain the process runs of the workspace in the path.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.list_process_runs200_response import ListProcessRuns200Response
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
    api_instance = robocorp.workspace.ProcessRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    process_id = 'process_id_example' # str | Process ID, if specified, the response will only contain the process runs from this process (optional)
    state = 'state_example' # str | State of process runs (optional)
    limit = 3.4 # float | Limit for paginated response (optional)

    try:
        # List process runs
        api_response = api_instance.list_process_runs(workspace_id, process_id=process_id, state=state, limit=limit)
        print("The response of ProcessRunApi->list_process_runs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProcessRunApi->list_process_runs: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **process_id** | **str**| Process ID, if specified, the response will only contain the process runs from this process | [optional] 
 **state** | **str**| State of process runs | [optional] 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**ListProcessRuns200Response**](ListProcessRuns200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Process Runs |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_process_run**
> StartProcessRun200Response start_process_run(workspace_id, process_id, start_process_run_request=start_process_run_request)

Start process run

Starts a process run for the requested process. You may choose to start a process run without work items, with specified work items, or with the work items that are waiting in the input queue of the specified process. 

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.start_process_run200_response import StartProcessRun200Response
from robocorp.workspace.models.start_process_run_request import StartProcessRunRequest
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
    api_instance = robocorp.workspace.ProcessRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the process resides.
    process_id = 'process_id_example' # str | The id of the process to start.
    start_process_run_request = robocorp.workspace.StartProcessRunRequest() # StartProcessRunRequest | Omitting the request body will start a process run with either the default work item, if configured, or an empty work item.  (optional)

    try:
        # Start process run
        api_response = api_instance.start_process_run(workspace_id, process_id, start_process_run_request=start_process_run_request)
        print("The response of ProcessRunApi->start_process_run:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProcessRunApi->start_process_run: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the process resides. | 
 **process_id** | **str**| The id of the process to start. | 
 **start_process_run_request** | [**StartProcessRunRequest**](StartProcessRunRequest.md)| Omitting the request body will start a process run with either the default work item, if configured, or an empty work item.  | [optional] 

### Return type

[**StartProcessRun200Response**](StartProcessRun200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Started Process Run |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |
**409** | Conflict |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_process_run_qs_auth**
> StartProcessRunQsAuth200Response start_process_run_qs_auth(workspace_id, process_id, token, any_valid_json, with_handshake=with_handshake)

Start process run (for integrations)

Starts a process run for the requested process. This endpoint is useful when you don't have control over the **headers** and / or **request body** of the caller and need a plain URL. This includes e.g. certain integration cases. The **full request body** will be provided as the input work item for the process run. The **API Key** must be provided as the value of the `token` query-string parameter. This endpoint supports **webhook handshakes** for added security. Currently we support the protocol employed by [Asana](https://asana.com/). If you are using Asana, use the `with_handshake=asana` query string parameter when constructing the URL to enable Asana webhook handshakes. 

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.any_valid_json import AnyValidJson
from robocorp.workspace.models.start_process_run_qs_auth200_response import StartProcessRunQsAuth200Response
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
    api_instance = robocorp.workspace.ProcessRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    process_id = 'process_id_example' # str | Process ID
    token = 'token_example' # str | Authorization token
    any_valid_json = robocorp.workspace.AnyValidJson() # AnyValidJson | Any valid JSON payload. The full request body is passed as a work item to the process run input. 
    with_handshake = 'with_handshake_example' # str | Handshake type (optional)

    try:
        # Start process run (for integrations)
        api_response = api_instance.start_process_run_qs_auth(workspace_id, process_id, token, any_valid_json, with_handshake=with_handshake)
        print("The response of ProcessRunApi->start_process_run_qs_auth:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProcessRunApi->start_process_run_qs_auth: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **process_id** | **str**| Process ID | 
 **token** | **str**| Authorization token | 
 **any_valid_json** | [**AnyValidJson**](AnyValidJson.md)| Any valid JSON payload. The full request body is passed as a work item to the process run input.  | 
 **with_handshake** | **str**| Handshake type | [optional] 

### Return type

[**StartProcessRunQsAuth200Response**](StartProcessRunQsAuth200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Started Process Run |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stop_process_run**
> StopProcessRun200Response stop_process_run(workspace_id, process_run_id, stop_process_run_request)

Stop process run

Stops the process run.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.stop_process_run200_response import StopProcessRun200Response
from robocorp.workspace.models.stop_process_run_request import StopProcessRunRequest
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
    api_instance = robocorp.workspace.ProcessRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the process run resides.
    process_run_id = 'process_run_id_example' # str | The id of the process run to stop.
    stop_process_run_request = robocorp.workspace.StopProcessRunRequest() # StopProcessRunRequest | Set whether or not to set the remaining work items as done or terminating the ongoing activity runs, as well as the reason for stopping the process run.

    try:
        # Stop process run
        api_response = api_instance.stop_process_run(workspace_id, process_run_id, stop_process_run_request)
        print("The response of ProcessRunApi->stop_process_run:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProcessRunApi->stop_process_run: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the process run resides. | 
 **process_run_id** | **str**| The id of the process run to stop. | 
 **stop_process_run_request** | [**StopProcessRunRequest**](StopProcessRunRequest.md)| Set whether or not to set the remaining work items as done or terminating the ongoing activity runs, as well as the reason for stopping the process run. | 

### Return type

[**StopProcessRun200Response**](StopProcessRun200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Stopped Process Run |  -  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

