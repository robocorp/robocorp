# workspace.WorkerApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_link_token**](WorkerApi.md#create_link_token) | **POST** /workspaces/{workspace_id}/workers/link-tokens | Create worker link token
[**delete_worker**](WorkerApi.md#delete_worker) | **DELETE** /workspaces/{workspace_id}/workers/{worker_id} | Delete worker
[**get_worker**](WorkerApi.md#get_worker) | **GET** /workspaces/{workspace_id}/workers/{worker_id} | Get worker
[**list_workers**](WorkerApi.md#list_workers) | **GET** /workspaces/{workspace_id}/workers | List workers
[**update_worker**](WorkerApi.md#update_worker) | **PUT** /workspaces/{workspace_id}/workers/{worker_id} | Update worker


# **create_link_token**
> LinkTokenResource create_link_token(workspace_id, create_link_token_request)

Create worker link token

Generates and returns a link token used to link a new worker to the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.create_link_token_request import CreateLinkTokenRequest
from workspace.models.link_token_resource import LinkTokenResource
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
    api_instance = workspace.WorkerApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker should reside.
    create_link_token_request = workspace.CreateLinkTokenRequest() # CreateLinkTokenRequest | 

    try:
        # Create worker link token
        api_response = api_instance.create_link_token(workspace_id, create_link_token_request)
        print("The response of WorkerApi->create_link_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerApi->create_link_token: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker should reside. | 
 **create_link_token_request** | [**CreateLinkTokenRequest**](CreateLinkTokenRequest.md)|  | 

### Return type

[**LinkTokenResource**](LinkTokenResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Worker Link Token |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_worker**
> DeleteWorker200Response delete_worker(workspace_id, worker_id)

Delete worker

Deletes the requested worker. This action is irreversible!

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.delete_worker200_response import DeleteWorker200Response
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
    api_instance = workspace.WorkerApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker resides.
    worker_id = 'worker_id_example' # str | The id of the worker to delete.

    try:
        # Delete worker
        api_response = api_instance.delete_worker(workspace_id, worker_id)
        print("The response of WorkerApi->delete_worker:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerApi->delete_worker: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker resides. | 
 **worker_id** | **str**| The id of the worker to delete. | 

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
**200** | Deleted Worker |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_worker**
> WorkerResource get_worker(workspace_id, worker_id)

Get worker

Returns a worker linked to the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.worker_resource import WorkerResource
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
    api_instance = workspace.WorkerApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker resides.
    worker_id = 'worker_id_example' # str | The id of the worker to retrieve.

    try:
        # Get worker
        api_response = api_instance.get_worker(workspace_id, worker_id)
        print("The response of WorkerApi->get_worker:\n")
        pprint(api_response)
    except Exception as e:
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

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Worker |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_workers**
> ListWorkers200Response list_workers(workspace_id, limit=limit)

List workers

Returns a list of all workers linked to the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.list_workers200_response import ListWorkers200Response
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
    api_instance = workspace.WorkerApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker resides.
    limit = 3.4 # float | Limit for paginated response (optional)

    try:
        # List workers
        api_response = api_instance.list_workers(workspace_id, limit=limit)
        print("The response of WorkerApi->list_workers:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerApi->list_workers: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker resides. | 
 **limit** | **float**| Limit for paginated response | [optional] 

### Return type

[**ListWorkers200Response**](ListWorkers200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Workers |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_worker**
> WorkerResource update_worker(workspace_id, worker_id, update_worker_request)

Update worker

Updates the requested worker by setting only the values defined in the request body.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.update_worker_request import UpdateWorkerRequest
from workspace.models.worker_resource import WorkerResource
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
    api_instance = workspace.WorkerApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker resides.
    worker_id = 'worker_id_example' # str | The id of the worker to update.
    update_worker_request = workspace.UpdateWorkerRequest() # UpdateWorkerRequest | The worker details to update.

    try:
        # Update worker
        api_response = api_instance.update_worker(workspace_id, worker_id, update_worker_request)
        print("The response of WorkerApi->update_worker:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerApi->update_worker: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker resides. | 
 **worker_id** | **str**| The id of the worker to update. | 
 **update_worker_request** | [**UpdateWorkerRequest**](UpdateWorkerRequest.md)| The worker details to update. | 

### Return type

[**WorkerResource**](WorkerResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Worker |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

