# workspace.StepRunApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_step_run**](StepRunApi.md#get_step_run) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id} | Get step run
[**get_step_run_artifact**](StepRunApi.md#get_step_run_artifact) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/artifacts/{artifact_id} | Get step run artifact
[**list_step_run_artifacts**](StepRunApi.md#list_step_run_artifacts) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/artifacts | List step run artifacts
[**list_step_run_console_messages**](StepRunApi.md#list_step_run_console_messages) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/console-messages | List step run console messages
[**list_step_run_events**](StepRunApi.md#list_step_run_events) | **GET** /workspaces/{workspace_id}/step-runs/{step_run_id}/events | List step run events
[**list_step_runs**](StepRunApi.md#list_step_runs) | **GET** /workspaces/{workspace_id}/step-runs | List step runs


# **get_step_run**
> StepRunResource get_step_run(workspace_id, step_run_id)

Get step run

Returns a specific step run from a process run.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.step_run_resource import StepRunResource
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
    api_instance = workspace.StepRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    step_run_id = 'step_run_id_example' # str | ID of the step run

    try:
        # Get step run
        api_response = api_instance.get_step_run(workspace_id, step_run_id)
        print("The response of StepRunApi->get_step_run:\n")
        pprint(api_response)
    except Exception as e:
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

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Step Run |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_step_run_artifact**
> GetStepRunArtifact200Response get_step_run_artifact(workspace_id, step_run_id, artifact_id)

Get step run artifact

Returns a step run artifact.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.get_step_run_artifact200_response import GetStepRunArtifact200Response
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
    api_instance = workspace.StepRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    step_run_id = 'step_run_id_example' # str | ID of the step run
    artifact_id = 'artifact_id_example' # str | ID of the artifact to retrieve

    try:
        # Get step run artifact
        api_response = api_instance.get_step_run_artifact(workspace_id, step_run_id, artifact_id)
        print("The response of StepRunApi->get_step_run_artifact:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StepRunApi->get_step_run_artifact: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **step_run_id** | **str**| ID of the step run | 
 **artifact_id** | **str**| ID of the artifact to retrieve | 

### Return type

[**GetStepRunArtifact200Response**](GetStepRunArtifact200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Artifact |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_step_run_artifacts**
> ListStepRunArtifacts200Response list_step_run_artifacts(workspace_id, step_run_id, limit=limit)

List step run artifacts

Returns the list of all artifacts for a step run.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.list_step_run_artifacts200_response import ListStepRunArtifacts200Response
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
    api_instance = workspace.StepRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    step_run_id = 'step_run_id_example' # str | Step Run ID
    limit = 3.4 # float | Limit for paginated response (optional)

    try:
        # List step run artifacts
        api_response = api_instance.list_step_run_artifacts(workspace_id, step_run_id, limit=limit)
        print("The response of StepRunApi->list_step_run_artifacts:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StepRunApi->list_step_run_artifacts: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **step_run_id** | **str**| Step Run ID | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**ListStepRunArtifacts200Response**](ListStepRunArtifacts200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Artifacts |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_step_run_console_messages**
> ListStepRunConsoleMessages200Response list_step_run_console_messages(workspace_id, step_run_id)

List step run console messages

Returns a paginated list of console messages for the step run.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.list_step_run_console_messages200_response import ListStepRunConsoleMessages200Response
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
    api_instance = workspace.StepRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    step_run_id = 'step_run_id_example' # str | Step Run ID

    try:
        # List step run console messages
        api_response = api_instance.list_step_run_console_messages(workspace_id, step_run_id)
        print("The response of StepRunApi->list_step_run_console_messages:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StepRunApi->list_step_run_console_messages: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **step_run_id** | **str**| Step Run ID | 

### Return type

[**ListStepRunConsoleMessages200Response**](ListStepRunConsoleMessages200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Step Run Console Messages |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_step_run_events**
> ListStepRunEvents200Response list_step_run_events(workspace_id, step_run_id, limit=limit)

List step run events

Returns the events of a step run.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.list_step_run_events200_response import ListStepRunEvents200Response
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
    api_instance = workspace.StepRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    step_run_id = 'step_run_id_example' # str | ID of the step run
    limit = 3.4 # float | Limit for paginated response (optional)

    try:
        # List step run events
        api_response = api_instance.list_step_run_events(workspace_id, step_run_id, limit=limit)
        print("The response of StepRunApi->list_step_run_events:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StepRunApi->list_step_run_events: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **step_run_id** | **str**| ID of the step run | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**ListStepRunEvents200Response**](ListStepRunEvents200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Events |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_step_runs**
> ListStepRuns200Response list_step_runs(workspace_id, process_run_id, limit=limit)

List step runs

Returns a paginated list of step runs.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.list_step_runs200_response import ListStepRuns200Response
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
    api_instance = workspace.StepRunApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    process_run_id = 'process_run_id_example' # str | Process Run ID
    limit = 3.4 # float | Limit for paginated response (optional)

    try:
        # List step runs
        api_response = api_instance.list_step_runs(workspace_id, process_run_id, limit=limit)
        print("The response of StepRunApi->list_step_runs:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling StepRunApi->list_step_runs: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **process_run_id** | **str**| Process Run ID | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**ListStepRuns200Response**](ListStepRuns200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Step Runs |  -  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

