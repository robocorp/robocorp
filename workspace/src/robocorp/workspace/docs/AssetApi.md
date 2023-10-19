# workspace.AssetApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_asset**](AssetApi.md#create_asset) | **POST** /workspaces/{workspace_id}/assets | Create new asset
[**create_asset_upload**](AssetApi.md#create_asset_upload) | **POST** /workspaces/{workspace_id}/assets/{asset_id}/uploads | Create asset upload
[**delete_asset**](AssetApi.md#delete_asset) | **DELETE** /workspaces/{workspace_id}/assets/{asset_id} | Delete asset
[**get_asset**](AssetApi.md#get_asset) | **GET** /workspaces/{workspace_id}/assets/{asset_id} | Get asset
[**get_asset_upload**](AssetApi.md#get_asset_upload) | **GET** /workspaces/{workspace_id}/assets/{asset_id}/uploads/{upload_id} | Get asset upload
[**list_assets**](AssetApi.md#list_assets) | **GET** /workspaces/{workspace_id}/assets | List assets


# **create_asset**
> EmptyAssetDetailsResource create_asset(workspace_id, update_worker_request)

Create new asset

Creating an asset is a multi-step process, see “Create an asset upload” to specify the data.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.empty_asset_details_resource import EmptyAssetDetailsResource
from workspace.models.update_worker_request import UpdateWorkerRequest
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
    api_instance = workspace.AssetApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker should reside.
    update_worker_request = workspace.UpdateWorkerRequest() # UpdateWorkerRequest | 

    try:
        # Create new asset
        api_response = api_instance.create_asset(workspace_id, update_worker_request)
        print("The response of AssetApi->create_asset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->create_asset: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker should reside. | 
 **update_worker_request** | [**UpdateWorkerRequest**](UpdateWorkerRequest.md)|  | 

### Return type

[**EmptyAssetDetailsResource**](EmptyAssetDetailsResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Asset |  * Access-Control-Allow-Origin -  <br>  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_asset_upload**
> CreateAssetUpload200Response create_asset_upload(workspace_id, asset_id, create_asset_upload_request)

Create asset upload

Create an upload for the requested asset payload. For payloads with less than 5MB you can upload the contents directly on the upload creation by specifying the data field. For larger uploads you can create the upload and use the returned upload URL for uploading the contents.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.create_asset_upload200_response import CreateAssetUpload200Response
from workspace.models.create_asset_upload_request import CreateAssetUploadRequest
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
    api_instance = workspace.AssetApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    asset_id = 'asset_id_example' # str | Asset ID or Asset Name prefixed with `name:` e.g. `name:my-asset-name`
    create_asset_upload_request = workspace.CreateAssetUploadRequest() # CreateAssetUploadRequest | 

    try:
        # Create asset upload
        api_response = api_instance.create_asset_upload(workspace_id, asset_id, create_asset_upload_request)
        print("The response of AssetApi->create_asset_upload:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->create_asset_upload: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **asset_id** | **str**| Asset ID or Asset Name prefixed with &#x60;name:&#x60; e.g. &#x60;name:my-asset-name&#x60; | 
 **create_asset_upload_request** | [**CreateAssetUploadRequest**](CreateAssetUploadRequest.md)|  | 

### Return type

[**CreateAssetUpload200Response**](CreateAssetUpload200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Asset Upload |  -  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_asset**
> DeleteWorker200Response delete_asset(workspace_id, asset_id)

Delete asset

Deletes the requested asset. This action is irreversible!

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
    api_instance = workspace.AssetApi(api_client)
    workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker resides.
    asset_id = 'asset_id_example' # str | Asset ID or Asset Name prefixed with `name:` e.g. `name:my-asset-name`

    try:
        # Delete asset
        api_response = api_instance.delete_asset(workspace_id, asset_id)
        print("The response of AssetApi->delete_asset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->delete_asset: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker resides. | 
 **asset_id** | **str**| Asset ID or Asset Name prefixed with &#x60;name:&#x60; e.g. &#x60;name:my-asset-name&#x60; | 

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
**200** | Deleted Asset |  * Access-Control-Allow-Origin -  <br>  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_asset**
> AssetDetailsResource get_asset(workspace_id, asset_id)

Get asset

Returns an asset for the requested workspace. The asset is returned including its payload.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.asset_details_resource import AssetDetailsResource
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
    api_instance = workspace.AssetApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    asset_id = 'asset_id_example' # str | Asset ID or Asset Name prefixed with `name:` e.g. `name:my-asset-name`

    try:
        # Get asset
        api_response = api_instance.get_asset(workspace_id, asset_id)
        print("The response of AssetApi->get_asset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->get_asset: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **asset_id** | **str**| Asset ID or Asset Name prefixed with &#x60;name:&#x60; e.g. &#x60;name:my-asset-name&#x60; | 

### Return type

[**AssetDetailsResource**](AssetDetailsResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Asset |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_asset_upload**
> AssetUploadResource get_asset_upload(workspace_id, asset_id, upload_id)

Get asset upload

Get the upload of an asset.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.asset_upload_resource import AssetUploadResource
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
    api_instance = workspace.AssetApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID
    asset_id = 'asset_id_example' # str | Asset ID
    upload_id = 'upload_id_example' # str | Payload Upload ID

    try:
        # Get asset upload
        api_response = api_instance.get_asset_upload(workspace_id, asset_id, upload_id)
        print("The response of AssetApi->get_asset_upload:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->get_asset_upload: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 
 **asset_id** | **str**| Asset ID | 
 **upload_id** | **str**| Payload Upload ID | 

### Return type

[**AssetUploadResource**](AssetUploadResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Asset Upload |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_assets**
> ListAssets200Response list_assets(workspace_id)

List assets

Returns a list of all assets linked to the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import workspace
from workspace.models.list_assets200_response import ListAssets200Response
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
    api_instance = workspace.AssetApi(api_client)
    workspace_id = 'workspace_id_example' # str | Workspace ID

    try:
        # List assets
        api_response = api_instance.list_assets(workspace_id)
        print("The response of AssetApi->list_assets:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetApi->list_assets: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 

### Return type

[**ListAssets200Response**](ListAssets200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Assets |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

