# swagger_client.TaskPackageApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_task_package**](TaskPackageApi.md#create_task_package) | **POST** /workspaces/{workspace_id}/task-packages | Create new task package
[**delete_task_package**](TaskPackageApi.md#delete_task_package) | **DELETE** /workspaces/{workspace_id}/task-packages/{task_package_id} | Delete task package
[**get_task_package_download_link**](TaskPackageApi.md#get_task_package_download_link) | **GET** /workspaces/{workspace_id}/task-packages/{task_package_id}/download | Get task package download link
[**get_task_package_upload_link**](TaskPackageApi.md#get_task_package_upload_link) | **GET** /workspaces/{workspace_id}/task-packages/{task_package_id}/upload | Get task package upload link

# **create_task_package**
> TaskPackageResource create_task_package(body, workspace_id)

Create new task package

Creates a new task package with the given name in the requested workspace.

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
api_instance = swagger_client.TaskPackageApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkspaceIdTaskpackagesBody() # WorkspaceIdTaskpackagesBody | The name of the task package to create
workspace_id = 'workspace_id_example' # str | The id of the workspace in which to create the task package

try:
    # Create new task package
    api_response = api_instance.create_task_package(body, workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TaskPackageApi->create_task_package: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkspaceIdTaskpackagesBody**](WorkspaceIdTaskpackagesBody.md)| The name of the task package to create | 
 **workspace_id** | **str**| The id of the workspace in which to create the task package | 

### Return type

[**TaskPackageResource**](TaskPackageResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_task_package**
> InlineResponse2001 delete_task_package(workspace_id, task_package_id)

Delete task package

Deletes a specific task package. This action is irreversible!

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
api_instance = swagger_client.TaskPackageApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the task package resides.
task_package_id = 'task_package_id_example' # str | The id of the task package to delete.

try:
    # Delete task package
    api_response = api_instance.delete_task_package(workspace_id, task_package_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TaskPackageApi->delete_task_package: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the task package resides. | 
 **task_package_id** | **str**| The id of the task package to delete. | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_task_package_download_link**
> TaskPackageDownloadLink get_task_package_download_link(workspace_id, task_package_id)

Get task package download link

Returns a URL to download the task package bundle.

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
api_instance = swagger_client.TaskPackageApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace in which the task package resides
task_package_id = 'task_package_id_example' # str | The id of the task package to get the download link for

try:
    # Get task package download link
    api_response = api_instance.get_task_package_download_link(workspace_id, task_package_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TaskPackageApi->get_task_package_download_link: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace in which the task package resides | 
 **task_package_id** | **str**| The id of the task package to get the download link for | 

### Return type

[**TaskPackageDownloadLink**](TaskPackageDownloadLink.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_task_package_upload_link**
> TaskPackageUploadLink get_task_package_upload_link(workspace_id, task_package_id)

Get task package upload link

Returns a URL + form data payload for uploading the task package bundle.

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
api_instance = swagger_client.TaskPackageApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace in which the task package resides
task_package_id = 'task_package_id_example' # str | The id of the task package to get the upload link for

try:
    # Get task package upload link
    api_response = api_instance.get_task_package_upload_link(workspace_id, task_package_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling TaskPackageApi->get_task_package_upload_link: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace in which the task package resides | 
 **task_package_id** | **str**| The id of the task package to get the upload link for | 

### Return type

[**TaskPackageUploadLink**](TaskPackageUploadLink.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

