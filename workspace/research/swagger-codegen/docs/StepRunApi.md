# swagger_client.StepRunApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_step_run**](StepRunApi.md#get_step_run) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id} | Get step run
[**get_step_run_artifact**](StepRunApi.md#get_step_run_artifact) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/artifacts/{artifact_id} | Get step run artifact
[**list_step_run_artifacts**](StepRunApi.md#list_step_run_artifacts) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/artifacts | List step run artifacts
[**list_step_run_console_messages**](StepRunApi.md#list_step_run_console_messages) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/console-messages | List step run console messages
[**list_step_run_events**](StepRunApi.md#list_step_run_events) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/events | List step run events
[**list_step_runs**](StepRunApi.md#list_step_runs) | **GET** /workspaces/{workspace_id}/process-runs/{process_run_id}/step-runs | List step runs of process run

# **get_step_run**
> StepRunResource get_step_run(workspace_id, step_run_id)

Get step run

Returns a specific step run from a process run.

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
api_instance = swagger_client.StepRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
step_run_id = 'step_run_id_example' # str | ID of the step run

try:
    # Get step run
    api_response = api_instance.get_step_run(workspace_id, step_run_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StepRunApi->get_step_run: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **step_run_id** | **str**| ID of the step run | 

### Return type

[**StepRunResource**](StepRunResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_step_run_artifact**
> InlineResponse20020 get_step_run_artifact(workspace_id, step_run_id, artifact_id)

Get step run artifact

Returns a step run artifact.

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
api_instance = swagger_client.StepRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
step_run_id = 'step_run_id_example' # str | ID of the step run
artifact_id = 'artifact_id_example' # str | ID of the artifact to retrieve

try:
    # Get step run artifact
    api_response = api_instance.get_step_run_artifact(workspace_id, step_run_id, artifact_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StepRunApi->get_step_run_artifact: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **step_run_id** | **str**| ID of the step run | 
 **artifact_id** | **str**| ID of the artifact to retrieve | 

### Return type

[**InlineResponse20020**](InlineResponse20020.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_step_run_artifacts**
> InlineResponse20019 list_step_run_artifacts(workspace_id, step_run_id)

List step run artifacts

Returns the list of all artifacts for a step run.

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
api_instance = swagger_client.StepRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
step_run_id = 'step_run_id_example' # str | Step Run ID

try:
    # List step run artifacts
    api_response = api_instance.list_step_run_artifacts(workspace_id, step_run_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StepRunApi->list_step_run_artifacts: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **step_run_id** | **str**| Step Run ID | 

### Return type

[**InlineResponse20019**](InlineResponse20019.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_step_run_console_messages**
> InlineResponse20021 list_step_run_console_messages(workspace_id, step_run_id)

List step run console messages

Returns all logged console messages for a step run.

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
api_instance = swagger_client.StepRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
step_run_id = 'step_run_id_example' # str | Step Run ID

try:
    # List step run console messages
    api_response = api_instance.list_step_run_console_messages(workspace_id, step_run_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StepRunApi->list_step_run_console_messages: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **step_run_id** | **str**| Step Run ID | 

### Return type

[**InlineResponse20021**](InlineResponse20021.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_step_run_events**
> InlineResponse20022 list_step_run_events(workspace_id, step_run_id)

List step run events

Returns the events of a step run.

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
api_instance = swagger_client.StepRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
step_run_id = 'step_run_id_example' # str | ID of the step run

try:
    # List step run events
    api_response = api_instance.list_step_run_events(workspace_id, step_run_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StepRunApi->list_step_run_events: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **step_run_id** | **str**| ID of the step run | 

### Return type

[**InlineResponse20022**](InlineResponse20022.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_step_runs**
> InlineResponse20018 list_step_runs(workspace_id, process_run_id)

List step runs of process run

Returns the list of all step runs for a process run.

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
api_instance = swagger_client.StepRunApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
process_run_id = 'process_run_id_example' # str | ID of the process run

try:
    # List step runs of process run
    api_response = api_instance.list_step_runs(workspace_id, process_run_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling StepRunApi->list_step_runs: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **process_run_id** | **str**| ID of the process run | 

### Return type

[**InlineResponse20018**](InlineResponse20018.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

