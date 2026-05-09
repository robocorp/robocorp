# swagger_client.WorkerApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_link_token**](WorkerApi.md#create_link_token) | **POST** /workspaces/{workspace_id}/workers/link-tokens | Create worker link token
[**delete_worker**](WorkerApi.md#delete_worker) | **DELETE** /workspaces/{workspace_id}/workers/{worker_id} | Delete worker
[**get_worker**](WorkerApi.md#get_worker) | **GET** /workspaces/{workspace_id}/workers/{worker_id} | Get worker
[**list_workers**](WorkerApi.md#list_workers) | **GET** /workspaces/{workspace_id}/workers | List workers
[**update_worker**](WorkerApi.md#update_worker) | **PUT** /workspaces/{workspace_id}/workers/{worker_id} | Update worker

# **create_link_token**
> LinkTokenResource create_link_token(body, workspace_id)

Create worker link token

Generates and returns a link token used to link a new worker to the requested workspace.

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
api_instance = swagger_client.WorkerApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkersLinktokensBody() # WorkersLinktokensBody | 
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker should reside.

try:
    # Create worker link token
    api_response = api_instance.create_link_token(body, workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerApi->create_link_token: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkersLinktokensBody**](WorkersLinktokensBody.md)|  | 
 **workspace_id** | **str**| The id of the workspace on which the worker should reside. | 

### Return type

[**LinkTokenResource**](LinkTokenResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_worker**
> InlineResponse2001 delete_worker(workspace_id, worker_id)

Delete worker

Deletes the requested worker. This action is irreversible!

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
api_instance = swagger_client.WorkerApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker resides.
worker_id = 'worker_id_example' # str | The id of the worker to delete.

try:
    # Delete worker
    api_response = api_instance.delete_worker(workspace_id, worker_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerApi->delete_worker: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker resides. | 
 **worker_id** | **str**| The id of the worker to delete. | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_worker**
> WorkerResource get_worker(workspace_id, worker_id)

Get worker

Returns a worker linked to the requested workspace.

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
api_instance = swagger_client.WorkerApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker resides.
worker_id = 'worker_id_example' # str | The id of the worker to retrieve.

try:
    # Get worker
    api_response = api_instance.get_worker(workspace_id, worker_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerApi->get_worker: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker resides. | 
 **worker_id** | **str**| The id of the worker to retrieve. | 

### Return type

[**WorkerResource**](WorkerResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_workers**
> InlineResponse200 list_workers(workspace_id)

List workers

Returns a list of all workers linked to the requested workspace.

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
api_instance = swagger_client.WorkerApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker resides.

try:
    # List workers
    api_response = api_instance.list_workers(workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerApi->list_workers: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker resides. | 

### Return type

[**InlineResponse200**](InlineResponse200.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_worker**
> WorkerResource update_worker(body, workspace_id, worker_id)

Update worker

Updates the requested worker by setting only the values defined in the request body.

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
api_instance = swagger_client.WorkerApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkersWorkerIdBody() # WorkersWorkerIdBody | The worker details to update.
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker resides.
worker_id = 'worker_id_example' # str | The id of the worker to update.

try:
    # Update worker
    api_response = api_instance.update_worker(body, workspace_id, worker_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerApi->update_worker: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkersWorkerIdBody**](WorkersWorkerIdBody.md)| The worker details to update. | 
 **workspace_id** | **str**| The id of the workspace on which the worker resides. | 
 **worker_id** | **str**| The id of the worker to update. | 

### Return type

[**WorkerResource**](WorkerResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

