# swagger_client.WorkerGroupApi

All URIs are relative to */*

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
> WorkerToGroupLinkListing add_worker_to_group(body, workspace_id, worker_group_id)

Add worker to worker group

Adds an existing worker to the requested worker group.

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkerGroupIdWorkersBody() # WorkerGroupIdWorkersBody | The id of the worker to add to the worker group

workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
worker_group_id = 'worker_group_id_example' # str | The id of the worker group to add the worker to

try:
    # Add worker to worker group
    api_response = api_instance.add_worker_to_group(body, workspace_id, worker_group_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerGroupApi->add_worker_to_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkerGroupIdWorkersBody**](WorkerGroupIdWorkersBody.md)| The id of the worker to add to the worker group
 | 
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to add the worker to | 

### Return type

[**WorkerToGroupLinkListing**](WorkerToGroupLinkListing.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_worker_group**
> WorkerGroupResource create_worker_group(body, workspace_id)

Create worker group

Creates a new worker group linked to the requested workspace.

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkspaceIdWorkergroupsBody() # WorkspaceIdWorkergroupsBody | The name of the worker group to create
workspace_id = 'workspace_id_example' # str | The id of the workspace under which the worker group should be created.

try:
    # Create worker group
    api_response = api_instance.create_worker_group(body, workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerGroupApi->create_worker_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkspaceIdWorkergroupsBody**](WorkspaceIdWorkergroupsBody.md)| The name of the worker group to create | 
 **workspace_id** | **str**| The id of the workspace under which the worker group should be created. | 

### Return type

[**WorkerGroupResource**](WorkerGroupResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_worker_group_link_token**
> WorkerGroupLinkTokenResource create_worker_group_link_token(body, workspace_id, worker_group_id)

Create worker group link token

Generates and returns a link token used to link a worker to the requested worker group. **Note:** For security reasons, the link token value can be retrieved in Control Room only. 

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkerGroupIdLinktokensBody() # WorkerGroupIdLinktokensBody | The name of the worker group link token to create

workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
worker_group_id = 'worker_group_id_example' # str | The id of the worker group to which the link token belongs.

try:
    # Create worker group link token
    api_response = api_instance.create_worker_group_link_token(body, workspace_id, worker_group_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerGroupApi->create_worker_group_link_token: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkerGroupIdLinktokensBody**](WorkerGroupIdLinktokensBody.md)| The name of the worker group link token to create
 | 
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to which the link token belongs. | 

### Return type

[**WorkerGroupLinkTokenResource**](WorkerGroupLinkTokenResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_worker_group**
> InlineResponse2001 delete_worker_group(workspace_id, worker_group_id)

Delete worker group

Deletes the requested worker group. This action is irreversible!

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
worker_group_id = 'worker_group_id_example' # str | The id of the worker group to delete.

try:
    # Delete worker group
    api_response = api_instance.delete_worker_group(workspace_id, worker_group_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerGroupApi->delete_worker_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to delete. | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_worker_group_link_token**
> InlineResponse2001 delete_worker_group_link_token(workspace_id, worker_group_id, link_token_id)

Delete worker group link token

Deletes the requested link token. This action is irreversible!

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
worker_group_id = 'worker_group_id_example' # str | The id of the worker group to which the link token belongs.
link_token_id = 'link_token_id_example' # str | The id of the worker group link token to delete.

try:
    # Delete worker group link token
    api_response = api_instance.delete_worker_group_link_token(workspace_id, worker_group_id, link_token_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerGroupApi->delete_worker_group_link_token: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to which the link token belongs. | 
 **link_token_id** | **str**| The id of the worker group link token to delete. | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_worker_group**
> WorkerGroupResource get_worker_group(workspace_id, worker_group_id)

Get worker group

Returns a worker group linked to the requested workspace.

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
worker_group_id = 'worker_group_id_example' # str | The id of the worker group to retrieve.

try:
    # Get worker group
    api_response = api_instance.get_worker_group(workspace_id, worker_group_id)
    pprint(api_response)
except ApiException as e:
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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_worker_group_link_token**
> WorkerGroupLinkTokenResource get_worker_group_link_token(workspace_id, worker_group_id, link_token_id)

Get worker group link token

Returns a link token for the requested work group. **Note**: For security reasons, the Link Token value can be retrieved in Control Room only. 

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
worker_group_id = 'worker_group_id_example' # str | The id of the worker group to which the link token belongs.
link_token_id = 'link_token_id_example' # str | The id of the worker group link token to retrieve.

try:
    # Get worker group link token
    api_response = api_instance.get_worker_group_link_token(workspace_id, worker_group_id, link_token_id)
    pprint(api_response)
except ApiException as e:
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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_worker_group_link_tokens**
> InlineResponse2003 list_worker_group_link_tokens(workspace_id, worker_group_id)

List worker group link tokens

Returns a list of all link tokens for the requested worker group. **Note:** For security reasons, the link token value can be retrieved in Control Room only. 

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
worker_group_id = 'worker_group_id_example' # str | The id of the worker group to which the link tokens belong.

try:
    # List worker group link tokens
    api_response = api_instance.list_worker_group_link_tokens(workspace_id, worker_group_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerGroupApi->list_worker_group_link_tokens: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to which the link tokens belong. | 

### Return type

[**InlineResponse2003**](InlineResponse2003.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_worker_groups**
> InlineResponse2002 list_worker_groups(workspace_id)

List worker groups

Returns a list of all worker groups linked to the requested workspace.

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace to list worker groups for

try:
    # List worker groups
    api_response = api_instance.list_worker_groups(workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerGroupApi->list_worker_groups: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace to list worker groups for | 

### Return type

[**InlineResponse2002**](InlineResponse2002.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **remove_worker_from_group**
> WorkerToGroupLinkListing remove_worker_from_group(workspace_id, worker_group_id, worker_id)

Remove worker from worker group

Removes an existing worker from the requested worker group.

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
worker_group_id = 'worker_group_id_example' # str | The id of the worker group to remove the worker from
worker_id = 'worker_id_example' # str | The id of the worker to remove from the worker group

try:
    # Remove worker from worker group
    api_response = api_instance.remove_worker_from_group(workspace_id, worker_group_id, worker_id)
    pprint(api_response)
except ApiException as e:
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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_worker_group**
> WorkerGroupResource update_worker_group(body, workspace_id, worker_group_id)

Update worker group

Updates the requested worker group by setting only the values defined in the request body.

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkergroupsWorkerGroupIdBody() # WorkergroupsWorkerGroupIdBody | The worker group details to update
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
worker_group_id = 'worker_group_id_example' # str | The id of the worker group to update.

try:
    # Update worker group
    api_response = api_instance.update_worker_group(body, workspace_id, worker_group_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerGroupApi->update_worker_group: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkergroupsWorkerGroupIdBody**](WorkergroupsWorkerGroupIdBody.md)| The worker group details to update | 
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to update. | 

### Return type

[**WorkerGroupResource**](WorkerGroupResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_worker_group_link_token**
> WorkerGroupLinkTokenResource update_worker_group_link_token(body, workspace_id, worker_group_id, link_token_id)

Update worker group link token

Updates a link token by setting only the values defined in the request body.

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
api_instance = swagger_client.WorkerGroupApi(swagger_client.ApiClient(configuration))
body = swagger_client.LinktokensLinkTokenIdBody() # LinktokensLinkTokenIdBody | The name of the worker group link token to update
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker group resides.
worker_group_id = 'worker_group_id_example' # str | The id of the worker group to which the link token belongs.
link_token_id = 'link_token_id_example' # str | The id of the worker group link token to update.

try:
    # Update worker group link token
    api_response = api_instance.update_worker_group_link_token(body, workspace_id, worker_group_id, link_token_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WorkerGroupApi->update_worker_group_link_token: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**LinktokensLinkTokenIdBody**](LinktokensLinkTokenIdBody.md)| The name of the worker group link token to update | 
 **workspace_id** | **str**| The id of the workspace on which the worker group resides. | 
 **worker_group_id** | **str**| The id of the worker group to which the link token belongs. | 
 **link_token_id** | **str**| The id of the worker group link token to update. | 

### Return type

[**WorkerGroupLinkTokenResource**](WorkerGroupLinkTokenResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

