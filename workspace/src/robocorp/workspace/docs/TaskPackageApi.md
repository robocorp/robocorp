# robocorp.workspace.TaskPackageApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_task_package**](TaskPackageApi.md#create_task_package) | **POST** /workspaces/{workspace_id}/task-packages | Create new task package
[**delete_task_package**](TaskPackageApi.md#delete_task_package) | **DELETE** /workspaces/{workspace_id}/task-packages/{task_package_id} | Delete task package
[**get_task_package**](TaskPackageApi.md#get_task_package) | **GET** /workspaces/{workspace_id}/task-packages/{task_package_id} | Get task package


# **create_task_package**
> TaskPackageResource create_task_package(workspace_id, create_task_package_request)

Create new task package

Creates a new task package with the given name in the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.create_task_package_request import CreateTaskPackageRequest
from robocorp.workspace.models.task_package_resource import TaskPackageResource
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
    api_instance = robocorp.workspace.TaskPackageApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace in which to create the task package
    create_task_package_request = robocorp.workspace.CreateTaskPackageRequest() # CreateTaskPackageRequest | The name of the task package to create

    try:
        # Create new task package
        api_response = api_instance.create_task_package(workspace_id, create_task_package_request)
        print("The response of TaskPackageApi->create_task_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TaskPackageApi->create_task_package: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace in which to create the task package | 
 **create_task_package_request** | [**CreateTaskPackageRequest**](CreateTaskPackageRequest.md)| The name of the task package to create | 

### Return type

[**TaskPackageResource**](TaskPackageResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Task Package |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_task_package**
> DeleteWorker200Response delete_task_package(workspace_id, task_package_id)

Delete task package

Deletes a specific task package. This action is irreversible!

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
    api_instance = robocorp.workspace.TaskPackageApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the task package resides.
    task_package_id = 'task_package_id_example' # str | The id of the task package to delete.

    try:
        # Delete task package
        api_response = api_instance.delete_task_package(workspace_id, task_package_id)
        print("The response of TaskPackageApi->delete_task_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TaskPackageApi->delete_task_package: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the task package resides. | 
 **task_package_id** | **str**| The id of the task package to delete. | 

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
**200** | Deleted Task Package |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_task_package**
> TaskPackageResource get_task_package(workspace_id, task_package_id)

Get task package

Returns a task package (zip type only), including the URL to download it as well as the URL and form data to upload a new version

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import robocorp.workspace
from robocorp.workspace.models.task_package_resource import TaskPackageResource
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
    api_instance = robocorp.workspace.TaskPackageApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the task package resides.
    task_package_id = 'task_package_id_example' # str | The id of the task package to retrieve.

    try:
        # Get task package
        api_response = api_instance.get_task_package(workspace_id, task_package_id)
        print("The response of TaskPackageApi->get_task_package:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TaskPackageApi->get_task_package: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the task package resides. | 
 **task_package_id** | **str**| The id of the task package to retrieve. | 

### Return type

[**TaskPackageResource**](TaskPackageResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Task Package |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

