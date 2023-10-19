# swagger_client.AssetApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_asset**](AssetApi.md#create_asset) | **POST** /workspaces/{workspace_id}/assets | Create new asset
[**create_asset_upload**](AssetApi.md#create_asset_upload) | **POST** /workspaces/{workspace_id}/assets/{asset_id}/uploads | Create asset upload
[**delete_asset**](AssetApi.md#delete_asset) | **DELETE** /workspaces/{workspace_id}/assets/{asset_id} | Delete asset
[**get_asset**](AssetApi.md#get_asset) | **GET** /workspaces/{workspace_id}/assets/{asset_id} | Get asset
[**get_asset_upload**](AssetApi.md#get_asset_upload) | **GET** /workspaces/{workspace_id}/assets/{asset_id}/uploads/{upload_id} | Get asset upload
[**list_assets**](AssetApi.md#list_assets) | **GET** /workspaces/{workspace_id}/assets | List assets

# **create_asset**
> EmptyAssetDetailsResource create_asset(body, workspace_id)

Create new asset

Creating an asset is a multi-step process, see “Create an asset upload” to specify the data.

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
api_instance = swagger_client.AssetApi(swagger_client.ApiClient(configuration))
body = swagger_client.WorkspaceIdAssetsBody() # WorkspaceIdAssetsBody | 
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker should reside.

try:
    # Create new asset
    api_response = api_instance.create_asset(body, workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AssetApi->create_asset: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**WorkspaceIdAssetsBody**](WorkspaceIdAssetsBody.md)|  | 
 **workspace_id** | **str**| The id of the workspace on which the worker should reside. | 

### Return type

[**EmptyAssetDetailsResource**](EmptyAssetDetailsResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_asset_upload**
> InlineResponse20016 create_asset_upload(body, workspace_id, asset_id)

Create asset upload

Create an upload for the requested asset payload. For payloads with less than 5MB you can upload the contents directly on the upload creation by specifying the data field. For larger uploads you can create the upload and use the returned upload URL for uploading the contents.

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
api_instance = swagger_client.AssetApi(swagger_client.ApiClient(configuration))
body = swagger_client.AssetIdUploadsBody() # AssetIdUploadsBody | 
workspace_id = 'workspace_id_example' # str | Workspace ID
asset_id = 'asset_id_example' # str | Asset ID or Asset Name prefixed with `name:` e.g. `name:my-asset-name`

try:
    # Create asset upload
    api_response = api_instance.create_asset_upload(body, workspace_id, asset_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AssetApi->create_asset_upload: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**AssetIdUploadsBody**](AssetIdUploadsBody.md)|  | 
 **workspace_id** | **str**| Workspace ID | 
 **asset_id** | **str**| Asset ID or Asset Name prefixed with &#x60;name:&#x60; e.g. &#x60;name:my-asset-name&#x60; | 

### Return type

[**InlineResponse20016**](InlineResponse20016.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_asset**
> InlineResponse2001 delete_asset(workspace_id, asset_id)

Delete asset

Deletes the requested asset. This action is irreversible!

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
api_instance = swagger_client.AssetApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The id of the workspace on which the worker resides.
asset_id = 'asset_id_example' # str | Asset ID or Asset Name prefixed with `name:` e.g. `name:my-asset-name`

try:
    # Delete asset
    api_response = api_instance.delete_asset(workspace_id, asset_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AssetApi->delete_asset: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The id of the workspace on which the worker resides. | 
 **asset_id** | **str**| Asset ID or Asset Name prefixed with &#x60;name:&#x60; e.g. &#x60;name:my-asset-name&#x60; | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_asset**
> AssetDetailsResource get_asset(workspace_id, asset_id)

Get asset

Returns an asset for the requested workspace. The asset is returned including its payload.

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
api_instance = swagger_client.AssetApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
asset_id = 'asset_id_example' # str | Asset ID or Asset Name prefixed with `name:` e.g. `name:my-asset-name`

try:
    # Get asset
    api_response = api_instance.get_asset(workspace_id, asset_id)
    pprint(api_response)
except ApiException as e:
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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_asset_upload**
> AssetUploadResource get_asset_upload(workspace_id, asset_id, upload_id)

Get asset upload

Get the upload of an asset.

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
api_instance = swagger_client.AssetApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID
asset_id = 'asset_id_example' # str | Asset ID
upload_id = 'upload_id_example' # str | Payload Upload ID

try:
    # Get asset upload
    api_response = api_instance.get_asset_upload(workspace_id, asset_id, upload_id)
    pprint(api_response)
except ApiException as e:
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

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_assets**
> InlineResponse20015 list_assets(workspace_id)

List assets

Returns a list of all assets linked to the requested workspace.

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
api_instance = swagger_client.AssetApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | Workspace ID

try:
    # List assets
    api_response = api_instance.list_assets(workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AssetApi->list_assets: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| Workspace ID | 

### Return type

[**InlineResponse20015**](InlineResponse20015.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

