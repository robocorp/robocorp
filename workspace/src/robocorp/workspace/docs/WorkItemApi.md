# robocorp.workspace.WorkItemApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_work_item**](WorkItemApi.md#create_work_item) | **POST** /workspaces/{workspace_id}/work-items | Create work item
[**create_work_item_file**](WorkItemApi.md#create_work_item_file) | **POST** /workspaces/{workspace_id}/work-items/{work_item_id}/files | Create work item file
[**get_work_item**](WorkItemApi.md#get_work_item) | **GET** /workspaces/{workspace_id}/work-items/{work_item_id} | Get work item
[**list_work_items**](WorkItemApi.md#list_work_items) | **GET** /workspaces/{workspace_id}/work-items | List work items
[**run_work_item_batch_operation**](WorkItemApi.md#run_work_item_batch_operation) | **POST** /workspaces/{workspace_id}/work-items/batch | Retry, delete or mark work items as done
[**update_work_item_payload**](WorkItemApi.md#update_work_item_payload) | **POST** /workspaces/{workspace_id}/work-items/{work_item_id}/payload | Update work item payload


# **create_work_item**
> WorkItemResource create_work_item(workspace_id, create_work_item_request)

Create work item

Create a work item for the requested process.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.create_work_item_request import CreateWorkItemRequest
from robocorp.workspace.models.work_item_resource import WorkItemResource
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
    api_instance = robocorp.workspace.WorkItemApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    create_work_item_request = robocorp.workspace.CreateWorkItemRequest() # CreateWorkItemRequest | Process work item payload

    try:
        # Create work item
        api_response = api_instance.create_work_item(workspace_id, create_work_item_request)
        print("The response of WorkItemApi->create_work_item:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkItemApi->create_work_item: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **create_work_item_request** | [**CreateWorkItemRequest**](CreateWorkItemRequest.md)| Process work item payload | 

### Return type

[**WorkItemResource**](WorkItemResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Work Item |  -  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |
**409** | Conflicting request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_work_item_file**
> CreateWorkItemFile200Response create_work_item_file(workspace_id, work_item_id, create_work_item_file_request)

Create work item file

Request to upload a work item file.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.create_work_item_file200_response import CreateWorkItemFile200Response
from robocorp.workspace.models.create_work_item_file_request import CreateWorkItemFileRequest
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
    api_instance = robocorp.workspace.WorkItemApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    work_item_id = 'work_item_id_example' # str | Work Item ID
    create_work_item_file_request = robocorp.workspace.CreateWorkItemFileRequest() # CreateWorkItemFileRequest | The name and size of work item file to create

    try:
        # Create work item file
        api_response = api_instance.create_work_item_file(workspace_id, work_item_id, create_work_item_file_request)
        print("The response of WorkItemApi->create_work_item_file:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkItemApi->create_work_item_file: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **work_item_id** | **str**| Work Item ID | 
 **create_work_item_file_request** | [**CreateWorkItemFileRequest**](CreateWorkItemFileRequest.md)| The name and size of work item file to create | 

### Return type

[**CreateWorkItemFile200Response**](CreateWorkItemFile200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Work Item File Upload Details |  -  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_work_item**
> WorkItemResource get_work_item(workspace_id, work_item_id)

Get work item

Returns a work item for the requested process. You can specify whether you want to also retrieve the work item's data (payload and/or files) by supplying the `include_data` query parameter. 

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.work_item_resource import WorkItemResource
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
    api_instance = robocorp.workspace.WorkItemApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    work_item_id = 'work_item_id_example' # str | Work Item ID

    try:
        # Get work item
        api_response = api_instance.get_work_item(workspace_id, work_item_id)
        print("The response of WorkItemApi->get_work_item:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkItemApi->get_work_item: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **work_item_id** | **str**| Work Item ID | 

### Return type

[**WorkItemResource**](WorkItemResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Work Item |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_work_items**
> ListWorkItems200Response list_work_items(workspace_id, process_id=process_id, process_run_id=process_run_id, state=state, limit=limit)

List work items

Returns a paginated list of work items. You can specify filtering work item by state, process_id and process_run_id using the query parameters. 

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.list_work_items200_response import ListWorkItems200Response
from robocorp.workspace.models.work_item_state import WorkItemState
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
    api_instance = robocorp.workspace.WorkItemApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    process_id = 'process_id_example' # str | Process ID (optional)
    process_run_id = 'process_run_id_example' # str | Process Run ID (optional)
    state = robocorp.workspace.WorkItemState() # WorkItemState | Work item state filter (optional)
    limit = 3.4 # float | Limit for paginated response (optional)

    try:
        # List work items
        api_response = api_instance.list_work_items(workspace_id, process_id=process_id, process_run_id=process_run_id, state=state, limit=limit)
        print("The response of WorkItemApi->list_work_items:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkItemApi->list_work_items: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **process_id** | **str**| Process ID | [optional] 
 **process_run_id** | **str**| Process Run ID | [optional] 
 **state** | [**WorkItemState**](.md)| Work item state filter | [optional] 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**ListWorkItems200Response**](ListWorkItems200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Work Items |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **run_work_item_batch_operation**
> StopProcessRun200Response run_work_item_batch_operation(workspace_id, run_work_item_batch_operation_request)

Retry, delete or mark work items as done

Run a batch operation on one or more work items. You can retry, delete or mark failed work items as done. 

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.run_work_item_batch_operation_request import RunWorkItemBatchOperationRequest
from robocorp.workspace.models.stop_process_run200_response import StopProcessRun200Response
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
    api_instance = robocorp.workspace.WorkItemApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    run_work_item_batch_operation_request = robocorp.workspace.RunWorkItemBatchOperationRequest() # RunWorkItemBatchOperationRequest | Work item batch operation

    try:
        # Retry, delete or mark work items as done
        api_response = api_instance.run_work_item_batch_operation(workspace_id, run_work_item_batch_operation_request)
        print("The response of WorkItemApi->run_work_item_batch_operation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkItemApi->run_work_item_batch_operation: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **run_work_item_batch_operation_request** | [**RunWorkItemBatchOperationRequest**](RunWorkItemBatchOperationRequest.md)| Work item batch operation | 

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
**200** | Work item batch operation result |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_work_item_payload**
> UpdateWorkItemPayloadRequest update_work_item_payload(workspace_id, work_item_id, update_work_item_payload_request)

Update work item payload

Update the payload for the requested work item.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.update_work_item_payload_request import UpdateWorkItemPayloadRequest
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
    api_instance = robocorp.workspace.WorkItemApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    work_item_id = 'work_item_id_example' # str | Work Item ID
    update_work_item_payload_request = robocorp.workspace.UpdateWorkItemPayloadRequest() # UpdateWorkItemPayloadRequest | The updated payload of work item

    try:
        # Update work item payload
        api_response = api_instance.update_work_item_payload(workspace_id, work_item_id, update_work_item_payload_request)
        print("The response of WorkItemApi->update_work_item_payload:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkItemApi->update_work_item_payload: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **work_item_id** | **str**| Work Item ID | 
 **update_work_item_payload_request** | [**UpdateWorkItemPayloadRequest**](UpdateWorkItemPayloadRequest.md)| The updated payload of work item | 

### Return type

[**UpdateWorkItemPayloadRequest**](UpdateWorkItemPayloadRequest.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Work Item Payload |  -  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
