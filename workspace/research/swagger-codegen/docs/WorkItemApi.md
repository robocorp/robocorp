# swagger_client.WorkItemApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_work_item**](WorkItemApi.md#create_work_item) | **POST** /workspaces/{workspace_id}/work-items | Create work item
[**create_work_item_file**](WorkItemApi.md#create_work_item_file) | **POST** /workspaces/{workspace_id}/work-items/{work_item_id}/files/upload | Create work item file
[**get_work_item**](WorkItemApi.md#get_work_item) | **GET** /workspaces/{workspace_id}/work-items/{work_item_id} | Get work item
[**list_process_run_work_items**](WorkItemApi.md#list_process_run_work_items) | **GET** /workspaces/{workspace_id}/process-runs/{process_run_id}/work-items | List work items of a process run
[**list_process_work_items**](WorkItemApi.md#list_process_work_items) | **GET** /workspaces/{workspace_id}/processes/{process_id}/work-items | List work items of process
[**run_work_item_batch_operation**](WorkItemApi.md#run_work_item_batch_operation) | **POST** /workspaces/{workspace_id}/work-items/batch | Retry, delete or mark work items as done
[**update_work_item_payload**](WorkItemApi.md#update_work_item_payload) | **PUT** /workspaces/{workspace_id}/work-items/{work_item_id}/payload | Update work item payload

# **create_work_item**
> WorkItemResource create_work_item(body, workspace_id)

Create work item

Create a work item for the requested process.

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
api_instance = swagger_client.WorkItemApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkspaceIdWorkitemsBody() # WorkspaceIdWorkitemsBody | Process work item payload
workspace_id = 'workspace_id_example' # str | Workspace ID

try:
    # Create work item
    api_response = api_instance.create_work_item(body, workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkItemApi->create_work_item: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkspaceIdWorkitemsBody**](WorkspaceIdWorkitemsBody.md)| Process work item payload | 
 **workspace_id** | **str**| Workspace ID | 

### Return type

[**WorkItemResource**](WorkItemResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_work_item_file**
> InlineResponse20012 create_work_item_file(body, workspace_id, work_item_id)

Create work item file

Request to upload a work item file.

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
api_instance = swagger_client.WorkItemApi(swagger_client.ApiClient(configuration))
body = swagger_client.FilesUploadBody() # FilesUploadBody | The name and size of work item file to create
workspace_id = 'workspace_id_example' # str | Workspace ID
work_item_id = 'work_item_id_example' # str | Work Item ID

try:
    # Create work item file
    api_response = api_instance.create_work_item_file(body, workspace_id, work_item_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkItemApi->create_work_item_file: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**FilesUploadBody**](FilesUploadBody.md)| The name and size of work item file to create | 
 **workspace_id** | **str**| Workspace ID | 
 **work_item_id** | **str**| Work Item ID | 

### Return type

[**InlineResponse20012**](InlineResponse20012.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_work_item**
> WorkItemResource get_work_item(workspace_id, work_item_id)

Get work item

Returns a work item for the requested process. You can specify whether you want to also retrieve the work item's data (payload and/or files) by supplying the `include_data` query parameter. 

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
api_instance = swagger_client.WorkItemApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
work_item_id = 'work_item_id_example' # str | Work Item ID

try:
    # Get work item
    api_response = api_instance.get_work_item(workspace_id, work_item_id)
    pprint(api_response)
except ApiException as e:
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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_process_run_work_items**
> InlineResponse20011 list_process_run_work_items(workspace_id, process_run_id, limit=limit, state=state)

List work items of a process run

Returns a paginated list of work items for the requested process run. You can specify filtering work item by state with `state` query parameter. 

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
api_instance = swagger_client.WorkItemApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
process_run_id = 'process_run_id_example' # str | Process Run ID
limit = 1.2 # float | Limit for paginated response (optional)
state = 'state_example' # str | Work item state filter (optional)

try:
    # List work items of a process run
    api_response = api_instance.list_process_run_work_items(workspace_id, process_run_id, limit=limit, state=state)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkItemApi->list_process_run_work_items: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **process_run_id** | **str**| Process Run ID | 
 **limit** | **float**| Limit for paginated response | [optional] 
 **state** | **str**| Work item state filter | [optional] 

### Return type

[**InlineResponse20011**](InlineResponse20011.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_process_work_items**
> InlineResponse20010 list_process_work_items(workspace_id, process_id, limit=limit, state=state)

List work items of process

Returns a paginated list of work items for the requested process. You can specify filtering work item by state with `state` query parameter. 

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
api_instance = swagger_client.WorkItemApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
process_id = 'process_id_example' # str | Process ID
limit = 1.2 # float | Limit for paginated response (optional)
state = swagger_client.WorkItemState() # WorkItemState | Work item state filter (optional)

try:
    # List work items of process
    api_response = api_instance.list_process_work_items(workspace_id, process_id, limit=limit, state=state)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkItemApi->list_process_work_items: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **process_id** | **str**| Process ID | 
 **limit** | **float**| Limit for paginated response | [optional] 
 **state** | [**WorkItemState**](.md)| Work item state filter | [optional] 

### Return type

[**InlineResponse20010**](InlineResponse20010.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **run_work_item_batch_operation**
> InlineResponse2009 run_work_item_batch_operation(body, workspace_id)

Retry, delete or mark work items as done

Run a batch operation on one or more work items. You can retry, delete or mark failed work items as done. 

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
api_instance = swagger_client.WorkItemApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkitemsBatchBody() # WorkitemsBatchBody | Work item batch operation
workspace_id = 'workspace_id_example' # str | Workspace ID

try:
    # Retry, delete or mark work items as done
    api_response = api_instance.run_work_item_batch_operation(body, workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkItemApi->run_work_item_batch_operation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkitemsBatchBody**](WorkitemsBatchBody.md)| Work item batch operation | 
 **workspace_id** | **str**| Workspace ID | 

### Return type

[**InlineResponse2009**](InlineResponse2009.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_work_item_payload**
> InlineResponse20013 update_work_item_payload(body, workspace_id, work_item_id)

Update work item payload

Update the payload for the requested work item.

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
api_instance = swagger_client.WorkItemApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkItemIdPayloadBody() # WorkItemIdPayloadBody | The updated payload of work item
workspace_id = 'workspace_id_example' # str | Workspace ID
work_item_id = 'work_item_id_example' # str | Work Item ID

try:
    # Update work item payload
    api_response = api_instance.update_work_item_payload(body, workspace_id, work_item_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkItemApi->update_work_item_payload: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkItemIdPayloadBody**](WorkItemIdPayloadBody.md)| The updated payload of work item | 
 **workspace_id** | **str**| Workspace ID | 
 **work_item_id** | **str**| Work Item ID | 

### Return type

[**InlineResponse20013**](InlineResponse20013.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

