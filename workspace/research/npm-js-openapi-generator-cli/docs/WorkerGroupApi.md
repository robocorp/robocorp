# openapi_client.WorkerGroupApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_worker_to_group**](WorkerGroupApi.md#add_worker_to_group) | **PUT** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/workers | Add worker to worker group
[**create_worker_group**](WorkerGroupApi.md#create_worker_group) | **POST** /workspaces/{workspace_id}/worker-groups | Create worker group
[**create_worker_group_link_token**](WorkerGroupApi.md#create_worker_group_link_token) | **POST** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/link-tokens | Create worker group link token
[**delete_worker_group**](WorkerGroupApi.md#delete_worker_group) | **DELETE** /workspaces/{workspace_id}/worker-groups/{worker_group_id} | Delete worker group
[**delete_worker_group_link_token**](WorkerGroupApi.md#delete_worker_group_link_token) | **DELETE** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/link-tokens/{link_token_id} | Delete worker group link token
[**get_worker_group**](WorkerGroupApi.md#get_worker_group) | **GET** /workspaces/{workspace_id}/worker-groups/{worker_group_id} | Get worker group
[**get_worker_group_link_token**](WorkerGroupApi.md#get_worker_group_link_token) | **GET** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/link-tokens/{link_token_id} | Get worker group link token
[**list_worker_group_link_tokens**](WorkerGroupApi.md#list_worker_group_link_tokens) | **GET** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/link-tokens | List worker group link tokens
[**list_worker_groups**](WorkerGroupApi.md#list_worker_groups) | **GET** /workspaces/{workspace_id}/worker-groups | List worker groups
[**remove_worker_from_group**](WorkerGroupApi.md#remove_worker_from_group) | **DELETE** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/workers/{worker_id} | Remove worker from worker group
[**update_worker_group**](WorkerGroupApi.md#update_worker_group) | **PUT** /workspaces/{workspace_id}/worker-groups/{worker_group_id} | Update worker group
[**update_worker_group_link_token**](WorkerGroupApi.md#update_worker_group_link_token) | **PUT** /workspaces/{workspace_id}/worker-groups/{worker_group_id}/link-tokens/{link_token_id} | Update worker group link token


# **add_worker_to_group**
> WorkerToGroupLinkListing add_worker_to_group(workspace_id, worker_group_id, add_worker_to_group_request)

Add worker to worker group

Adds an existing worker to the requested worker group.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.add_worker_to_group_request import AddWorkerToGroupRequest
from openapi_client.models.worker_to_group_link_listing import WorkerToGroupLinkListing
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
    worker_group_id = 'worker_group_id_example' # str | The id of the worker group to add the worker to
    add_worker_to_group_request = openapi_client.AddWorkerToGroupRequest() # AddWorkerToGroupRequest | The id of the worker to add to the worker group 

    try:
        # Add worker to worker group
        api_response = api_instance.add_worker_to_group(workspace_id, worker_group_id, add_worker_to_group_request)
        print("The response of WorkerGroupApi->add_worker_to_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->add_worker_to_group: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to add the worker to | 
 **add_worker_to_group_request** | [**AddWorkerToGroupRequest**](AddWorkerToGroupRequest.md)| The id of the worker to add to the worker group  | 

### Return type

[**WorkerToGroupLinkListing**](WorkerToGroupLinkListing.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Worker Group Link Listing |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_worker_group**
> WorkerGroupResource create_worker_group(workspace_id, update_worker_request)

Create worker group

Creates a new worker group linked to the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.update_worker_request import UpdateWorkerRequest
from openapi_client.models.worker_group_resource import WorkerGroupResource
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace under which the worker group should be created.
    update_worker_request = openapi_client.UpdateWorkerRequest() # UpdateWorkerRequest | The name of the worker group to create

    try:
        # Create worker group
        api_response = api_instance.create_worker_group(workspace_id, update_worker_request)
        print("The response of WorkerGroupApi->create_worker_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->create_worker_group: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace under which the worker group should be created. | 
 **update_worker_request** | [**UpdateWorkerRequest**](UpdateWorkerRequest.md)| The name of the worker group to create | 

### Return type

[**WorkerGroupResource**](WorkerGroupResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Worker Group |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_worker_group_link_token**
> WorkerGroupLinkTokenResource create_worker_group_link_token(workspace_id, worker_group_id, create_worker_group_link_token_request)

Create worker group link token

Generates and returns a link token used to link a worker to the requested worker group. **Note:** For security reasons, the link token value can be retrieved in Control Room only. 

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.create_worker_group_link_token_request import CreateWorkerGroupLinkTokenRequest
from openapi_client.models.worker_group_link_token_resource import WorkerGroupLinkTokenResource
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
    worker_group_id = 'worker_group_id_example' # str | The id of the worker group to which the link token belongs.
    create_worker_group_link_token_request = openapi_client.CreateWorkerGroupLinkTokenRequest() # CreateWorkerGroupLinkTokenRequest | The name of the worker group link token to create 

    try:
        # Create worker group link token
        api_response = api_instance.create_worker_group_link_token(workspace_id, worker_group_id, create_worker_group_link_token_request)
        print("The response of WorkerGroupApi->create_worker_group_link_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->create_worker_group_link_token: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to which the link token belongs. | 
 **create_worker_group_link_token_request** | [**CreateWorkerGroupLinkTokenRequest**](CreateWorkerGroupLinkTokenRequest.md)| The name of the worker group link token to create  | 

### Return type

[**WorkerGroupLinkTokenResource**](WorkerGroupLinkTokenResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Worker Group Link Token |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_worker_group**
> DeleteWorker200Response delete_worker_group(workspace_id, worker_group_id)

Delete worker group

Deletes the requested worker group. This action is irreversible!

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.delete_worker200_response import DeleteWorker200Response
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
    worker_group_id = 'worker_group_id_example' # str | The id of the worker group to delete.

    try:
        # Delete worker group
        api_response = api_instance.delete_worker_group(workspace_id, worker_group_id)
        print("The response of WorkerGroupApi->delete_worker_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->delete_worker_group: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to delete. | 

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
**200** | Deleted Worker Group |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_worker_group_link_token**
> DeleteWorker200Response delete_worker_group_link_token(workspace_id, worker_group_id, link_token_id)

Delete worker group link token

Deletes the requested link token. This action is irreversible!

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.delete_worker200_response import DeleteWorker200Response
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
    worker_group_id = 'worker_group_id_example' # str | The id of the worker group to which the link token belongs.
    link_token_id = 'link_token_id_example' # str | The id of the worker group link token to delete.

    try:
        # Delete worker group link token
        api_response = api_instance.delete_worker_group_link_token(workspace_id, worker_group_id, link_token_id)
        print("The response of WorkerGroupApi->delete_worker_group_link_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->delete_worker_group_link_token: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to which the link token belongs. | 
 **link_token_id** | **str**| The id of the worker group link token to delete. | 

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
**200** | Deleted Worker Group Link Token |  * Access-Control-Allow-Origin -  <br>  |
**400** | Forbidden |  -  |
**403** | Forbidden |  -  |
**404** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_worker_group**
> WorkerGroupResource get_worker_group(workspace_id, worker_group_id)

Get worker group

Returns a worker group linked to the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.worker_group_resource import WorkerGroupResource
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
    worker_group_id = 'worker_group_id_example' # str | The id of the worker group to retrieve.

    try:
        # Get worker group
        api_response = api_instance.get_worker_group(workspace_id, worker_group_id)
        print("The response of WorkerGroupApi->get_worker_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->get_worker_group: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to retrieve. | 

### Return type

[**WorkerGroupResource**](WorkerGroupResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Worker Group |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_worker_group_link_token**
> WorkerGroupLinkTokenResource get_worker_group_link_token(workspace_id, worker_group_id, link_token_id)

Get worker group link token

Returns a link token for the requested work group. **Note**: For security reasons, the Link Token value can be retrieved in Control Room only. 

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.worker_group_link_token_resource import WorkerGroupLinkTokenResource
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
    worker_group_id = 'worker_group_id_example' # str | The id of the worker group to which the link token belongs.
    link_token_id = 'link_token_id_example' # str | The id of the worker group link token to retrieve.

    try:
        # Get worker group link token
        api_response = api_instance.get_worker_group_link_token(workspace_id, worker_group_id, link_token_id)
        print("The response of WorkerGroupApi->get_worker_group_link_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->get_worker_group_link_token: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to which the link token belongs. | 
 **link_token_id** | **str**| The id of the worker group link token to retrieve. | 

### Return type

[**WorkerGroupLinkTokenResource**](WorkerGroupLinkTokenResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Worker Group Link Token |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_worker_group_link_tokens**
> ListWorkerGroupLinkTokens200Response list_worker_group_link_tokens(workspace_id, worker_group_id)

List worker group link tokens

Returns a list of all link tokens for the requested worker group. **Note:** For security reasons, the link token value can be retrieved in Control Room only. 

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.list_worker_group_link_tokens200_response import ListWorkerGroupLinkTokens200Response
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
    worker_group_id = 'worker_group_id_example' # str | The id of the worker group to which the link tokens belong.

    try:
        # List worker group link tokens
        api_response = api_instance.list_worker_group_link_tokens(workspace_id, worker_group_id)
        print("The response of WorkerGroupApi->list_worker_group_link_tokens:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->list_worker_group_link_tokens: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to which the link tokens belong. | 

### Return type

[**ListWorkerGroupLinkTokens200Response**](ListWorkerGroupLinkTokens200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Worker Group Link Tokens |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_worker_groups**
> ListWorkerGroups200Response list_worker_groups(workspace_id)

List worker groups

Returns a list of all worker groups linked to the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.list_worker_groups200_response import ListWorkerGroups200Response
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace to list worker groups for

    try:
        # List worker groups
        api_response = api_instance.list_worker_groups(workspace_id)
        print("The response of WorkerGroupApi->list_worker_groups:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->list_worker_groups: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace to list worker groups for | 

### Return type

[**ListWorkerGroups200Response**](ListWorkerGroups200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Worker Groups |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_worker_from_group**
> WorkerToGroupLinkListing remove_worker_from_group(workspace_id, worker_group_id, worker_id)

Remove worker from worker group

Removes an existing worker from the requested worker group.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.worker_to_group_link_listing import WorkerToGroupLinkListing
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
    worker_group_id = 'worker_group_id_example' # str | The id of the worker group to remove the worker from
    worker_id = 'worker_id_example' # str | The id of the worker to remove from the worker group

    try:
        # Remove worker from worker group
        api_response = api_instance.remove_worker_from_group(workspace_id, worker_group_id, worker_id)
        print("The response of WorkerGroupApi->remove_worker_from_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->remove_worker_from_group: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to remove the worker from | 
 **worker_id** | **str**| The id of the worker to remove from the worker group | 

### Return type

[**WorkerToGroupLinkListing**](WorkerToGroupLinkListing.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Worker Group Link Listing |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_worker_group**
> WorkerGroupResource update_worker_group(workspace_id, worker_group_id, update_worker_request)

Update worker group

Updates the requested worker group by setting only the values defined in the request body.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.update_worker_request import UpdateWorkerRequest
from openapi_client.models.worker_group_resource import WorkerGroupResource
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
    worker_group_id = 'worker_group_id_example' # str | The id of the worker group to update.
    update_worker_request = openapi_client.UpdateWorkerRequest() # UpdateWorkerRequest | The worker group details to update

    try:
        # Update worker group
        api_response = api_instance.update_worker_group(workspace_id, worker_group_id, update_worker_request)
        print("The response of WorkerGroupApi->update_worker_group:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->update_worker_group: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to update. | 
 **update_worker_request** | [**UpdateWorkerRequest**](UpdateWorkerRequest.md)| The worker group details to update | 

### Return type

[**WorkerGroupResource**](WorkerGroupResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Worker Group |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_worker_group_link_token**
> WorkerGroupLinkTokenResource update_worker_group_link_token(workspace_id, worker_group_id, link_token_id, create_worker_group_link_token_request)

Update worker group link token

Updates a link token by setting only the values defined in the request body.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.create_worker_group_link_token_request import CreateWorkerGroupLinkTokenRequest
from openapi_client.models.worker_group_link_token_resource import WorkerGroupLinkTokenResource
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
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
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.WorkerGroupApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
    worker_group_id = 'worker_group_id_example' # str | The id of the worker group to which the link token belongs.
    link_token_id = 'link_token_id_example' # str | The id of the worker group link token to update.
    create_worker_group_link_token_request = openapi_client.CreateWorkerGroupLinkTokenRequest() # CreateWorkerGroupLinkTokenRequest | The name of the worker group link token to update

    try:
        # Update worker group link token
        api_response = api_instance.update_worker_group_link_token(workspace_id, worker_group_id, link_token_id, create_worker_group_link_token_request)
        print("The response of WorkerGroupApi->update_worker_group_link_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkerGroupApi->update_worker_group_link_token: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to which the link token belongs. | 
 **link_token_id** | **str**| The id of the worker group link token to update. | 
 **create_worker_group_link_token_request** | [**CreateWorkerGroupLinkTokenRequest**](CreateWorkerGroupLinkTokenRequest.md)| The name of the worker group link token to update | 

### Return type

[**WorkerGroupLinkTokenResource**](WorkerGroupLinkTokenResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Worker Group Link Token |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

