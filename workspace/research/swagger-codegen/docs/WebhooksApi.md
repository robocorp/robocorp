# swagger_client.WebhooksApi

All URIs are relative to */*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_webhook**](WebhooksApi.md#create_webhook) | **POST** /workspaces/{workspace_id}/webhooks | Create Process webhook
[**delete_webhook**](WebhooksApi.md#delete_webhook) | **DELETE** /workspaces/{workspace_id}/webhooks/{webhook_id} | Delete webhook
[**get_webhook**](WebhooksApi.md#get_webhook) | **GET** /workspaces/{workspace_id}/webhooks/{webhook_id} | Get Webhook
[**list_webhooks**](WebhooksApi.md#list_webhooks) | **GET** /workspaces/{workspace_id}/webhooks | List Webhooks

# **create_webhook**
> WebhookResource create_webhook(body, workspace_id)

Create Process webhook

Creates a process webhook for the requested workspace.

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
api_instance = swagger_client.WebhooksApi(swagger_client.ApiClient(configuration))
body = swagger_client.ProcessWebhookPayload() # ProcessWebhookPayload | 
workspace_id = 'workspace_id_example' # str | The ID of the workspace

try:
    # Create Process webhook
    api_response = api_instance.create_webhook(body, workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WebhooksApi->create_webhook: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**ProcessWebhookPayload**](ProcessWebhookPayload.md)|  | 
 **workspace_id** | **str**| The ID of the workspace | 

### Return type

[**WebhookResource**](WebhookResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_webhook**
> InlineResponse2001 delete_webhook(workspace_id, webhook_id)

Delete webhook

Deletes the requested webhook. This action is irreversible!

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
api_instance = swagger_client.WebhooksApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The ID of the workspace
webhook_id = 'webhook_id_example' # str | The ID of the webhook

try:
    # Delete webhook
    api_response = api_instance.delete_webhook(workspace_id, webhook_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WebhooksApi->delete_webhook: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The ID of the workspace | 
 **webhook_id** | **str**| The ID of the webhook | 

### Return type

[**InlineResponse2001**](InlineResponse2001.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_webhook**
> WebhookResource get_webhook(workspace_id, webhook_id)

Get Webhook

Returns a webhook for the requested workspace.

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
api_instance = swagger_client.WebhooksApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The ID of the workspace
webhook_id = 'webhook_id_example' # str | The ID of the webhook

try:
    # Get Webhook
    api_response = api_instance.get_webhook(workspace_id, webhook_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WebhooksApi->get_webhook: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The ID of the workspace | 
 **webhook_id** | **str**| The ID of the webhook | 

### Return type

[**WebhookResource**](WebhookResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_webhooks**
> InlineResponse20017 list_webhooks(workspace_id)

List Webhooks

Retrieves a list of all webhooks for the requested workspace.

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
api_instance = swagger_client.WebhooksApi(swagger_client.ApiClient(configuration))
workspace_id = 'workspace_id_example' # str | The ID of the workspace

try:
    # List Webhooks
    api_response = api_instance.list_webhooks(workspace_id)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling WebhooksApi->list_webhooks: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The ID of the workspace | 

### Return type

[**InlineResponse20017**](InlineResponse20017.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

