# swagger_client.ProcessRunApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_process_run**](ProcessRunApi.md#delete_process_run) | **DELETE** /workspaces/{workspace_id}/process-runs/{process_run_id} | Delete process run
[**get_process_run**](ProcessRunApi.md#get_process_run) | **GET** /workspaces/{workspace_id}/process-runs/{process_run_id} | Get process run
[**list_process_process_runs**](ProcessRunApi.md#list_process_process_runs) | **GET** /workspaces/{workspace_id}/processes/{process_id}/process-runs | List process runs of process
[**list_process_run_outputs**](ProcessRunApi.md#list_process_run_outputs) | **GET** /workspaces/{workspace_id}/process-runs/{process_run_id}/outputs | List output work items
[**list_workspace_process_runs**](ProcessRunApi.md#list_workspace_process_runs) | **GET** /workspaces/{workspace_id}/process-runs | List process runs
[**start_process_run**](ProcessRunApi.md#start_process_run) | **POST** /workspaces/{workspace_id}/processes/{process_id}/process-runs | Start process run
[**start_process_run_qs_auth**](ProcessRunApi.md#start_process_run_qs_auth) | **POST** /workspaces/{workspace_id}/processes/{process_id}/process-runs-integrations | Start process run (for integrations)
[**stop_process_run**](ProcessRunApi.md#stop_process_run) | **POST** /workspaces/{workspace_id}/process-runs/{process_run_id}/stop | Stop process run

# **delete_process_run**
> InlineResponse2001 delete_process_run(workspace_id, process_run_id)

Delete process run

Deletes a process run. This action is irreversible!

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
api_instance = swagger_client.ProcessRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the robot resides.
process_run_id = 'process_run_id_example' # str | The id of the process run to delete.

try:
    # Delete process run
    api_response = api_instance.delete_process_run(workspace_id, process_run_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProcessRunApi->delete_process_run: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the robot resides. | 
 **process_run_id** | **str**| The id of the process run to delete. | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_process_run**
> ProcessRunResource get_process_run(workspace_id, process_run_id)

Get process run

Returns a process run

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
api_instance = swagger_client.ProcessRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
process_run_id = 'process_run_id_example' # str | ID of the process run

try:
    # Get process run
    api_response = api_instance.get_process_run(workspace_id, process_run_id)
    pprint(api_response)
except ApiException as e:
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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_process_process_runs**
> InlineResponse2004 list_process_process_runs(workspace_id, process_id, limit=limit)

List process runs of process

Returns a list of all process runs linked to the requested process.

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
api_instance = swagger_client.ProcessRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
process_id = 'process_id_example' # str | Process ID
limit = 1.2 # float | Limit for paginated response (optional)

try:
    # List process runs of process
    api_response = api_instance.list_process_process_runs(workspace_id, process_id, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProcessRunApi->list_process_process_runs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **process_id** | **str**| Process ID | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**InlineResponse2004**](InlineResponse2004.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_process_run_outputs**
> InlineResponse20014 list_process_run_outputs(workspace_id, process_run_id, limit=limit)

List output work items

Returns a list of all output work items for the requested process run.

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
api_instance = swagger_client.ProcessRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the process resides.
process_run_id = 'process_run_id_example' # str | The id of the process run for which to list the outputs.
limit = 1.2 # float | Limit for paginated response (optional)

try:
    # List output work items
    api_response = api_instance.list_process_run_outputs(workspace_id, process_run_id, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProcessRunApi->list_process_run_outputs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the process resides. | 
 **process_run_id** | **str**| The id of the process run for which to list the outputs. | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**InlineResponse20014**](InlineResponse20014.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_workspace_process_runs**
> InlineResponse2004 list_workspace_process_runs(workspace_id, state=state, limit=limit)

List process runs

Returns a paginated list of process runs linked to the requested workspace.

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
api_instance = swagger_client.ProcessRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
state = 'state_example' # str | State of process runs (optional)
limit = 1.2 # float | Limit for paginated response (optional)

try:
    # List process runs
    api_response = api_instance.list_workspace_process_runs(workspace_id, state=state, limit=limit)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProcessRunApi->list_workspace_process_runs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **state** | **str**| State of process runs | [optional] 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**InlineResponse2004**](InlineResponse2004.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_process_run**
> InlineResponse2006 start_process_run(workspace_id, process_id, body=body)

Start process run

Starts a process run for the requested process. You may choose to start a process run without work items, with specified work items, or with the work items that are waiting in the input queue of the specified process. 

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
api_instance = swagger_client.ProcessRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the process resides.
process_id = 'process_id_example' # str | The id of the process to start.
body = swagger_client.ProcessIdProcessrunsBody() # ProcessIdProcessrunsBody | Omitting the request body will start a process run with either the default work item, if configured, or an empty work item.
 (optional)

try:
    # Start process run
    api_response = api_instance.start_process_run(workspace_id, process_id, body=body)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProcessRunApi->start_process_run: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the process resides. | 
 **process_id** | **str**| The id of the process to start. | 
 **body** | [**ProcessIdProcessrunsBody**](ProcessIdProcessrunsBody.md)| Omitting the request body will start a process run with either the default work item, if configured, or an empty work item.
 | [optional] 

### Return type

[**InlineResponse2006**](InlineResponse2006.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **start_process_run_qs_auth**
> InlineResponse2005 start_process_run_qs_auth(body, token, workspace_id, process_id, with_handshake=with_handshake)

Start process run (for integrations)

Starts a process run for the requested process. This endpoint is useful when you don't have control over the **headers** and / or **request body** of the caller and need a plain URL. This includes e.g. certain integration cases. The **full request body** will be provided as the input work item for the process run. The **API Key** must be provided as the value of the `token` query-string parameter. This endpoint supports **webhook handshakes** for added security. Currently we support the protocol employed by [Asana](https://asana.com/). If you are using Asana, use the `with_handshake=asana` query string parameter when constructing the URL to enable Asana webhook handshakes. 

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
api_instance = swagger_client.ProcessRunApi(swagger_client.ApiClient(configuration))
body = swagger_client.AnyValidJson() # AnyValidJson | Any valid JSON payload.
The full request body is passed as a work item to the process run input.

token = 'token_example' # str | Authorization token
workspace_id = 'workspace_id_example' # str | Workspace ID
process_id = 'process_id_example' # str | Process ID
with_handshake = 'with_handshake_example' # str | Handshake type (optional)

try:
    # Start process run (for integrations)
    api_response = api_instance.start_process_run_qs_auth(body, token, workspace_id, process_id, with_handshake=with_handshake)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProcessRunApi->start_process_run_qs_auth: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AnyValidJson**](AnyValidJson.md)| Any valid JSON payload.
The full request body is passed as a work item to the process run input.
 | 
 **token** | **str**| Authorization token | 
 **workspace_id** | **str**| Workspace ID | 
 **process_id** | **str**| Process ID | 
 **with_handshake** | **str**| Handshake type | [optional] 

### Return type

[**InlineResponse2005**](InlineResponse2005.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stop_process_run**
> InlineResponse2007 stop_process_run(body, workspace_id, process_run_id)

Stop process run

Stops the process run.

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
api_instance = swagger_client.ProcessRunApi(swagger_client.ApiClient(configuration))
body = swagger_client.ProcessRunIdStopBody() # ProcessRunIdStopBody | Set whether or not to set the remaining work items as done or terminating the ongoing activity runs, as well as the reason for stopping the process run.
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the process resides.
process_run_id = 'process_run_id_example' # str | The id of the process run to stop.

try:
    # Stop process run
    api_response = api_instance.stop_process_run(body, workspace_id, process_run_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ProcessRunApi->stop_process_run: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ProcessRunIdStopBody**](ProcessRunIdStopBody.md)| Set whether or not to set the remaining work items as done or terminating the ongoing activity runs, as well as the reason for stopping the process run. | 
 **workspace_id** | **str**| The id of the workspace on which the process resides. | 
 **process_run_id** | **str**| The id of the process run to stop. | 

### Return type

[**InlineResponse2007**](InlineResponse2007.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

