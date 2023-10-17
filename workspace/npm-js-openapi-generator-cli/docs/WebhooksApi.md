# openapi_client.WebhooksApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_webhook**](WebhooksApi.md#create_webhook) | **POST** /workspaces/{workspace_id}/webhooks | Create Process webhook
[**delete_webhook**](WebhooksApi.md#delete_webhook) | **DELETE** /workspaces/{workspace_id}/webhooks/{webhook_id} | Delete webhook
[**get_webhook**](WebhooksApi.md#get_webhook) | **GET** /workspaces/{workspace_id}/webhooks/{webhook_id} | Get Webhook
[**list_webhooks**](WebhooksApi.md#list_webhooks) | **GET** /workspaces/{workspace_id}/webhooks | List Webhooks


# **create_webhook**
> WebhookResource create_webhook(workspace_id, process_webhook_payload)

Create Process webhook

Creates a process webhook for the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.process_webhook_payload import ProcessWebhookPayload
from openapi_client.models.webhook_resource import WebhookResource
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
    api_instance = openapi_client.WebhooksApi(api_client)
    workspace_id = 'workspace_id_example' # str | The ID of the workspace
    process_webhook_payload = openapi_client.ProcessWebhookPayload() # ProcessWebhookPayload | 

    try:
        # Create Process webhook
        api_response = api_instance.create_webhook(workspace_id, process_webhook_payload)
        print("The response of WebhooksApi->create_webhook:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->create_webhook: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The ID of the workspace | 
 **process_webhook_payload** | [**ProcessWebhookPayload**](ProcessWebhookPayload.md)|  | 

### Return type

[**WebhookResource**](WebhookResource.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Webhook |  -  |
**400** | Bad Request |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_webhook**
> DeleteWorker200Response delete_webhook(workspace_id, webhook_id)

Delete webhook

Deletes the requested webhook. This action is irreversible!

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
    api_instance = openapi_client.WebhooksApi(api_client)
    workspace_id = 'workspace_id_example' # str | The ID of the workspace
    webhook_id = 'webhook_id_example' # str | The ID of the webhook

    try:
        # Delete webhook
        api_response = api_instance.delete_webhook(workspace_id, webhook_id)
        print("The response of WebhooksApi->delete_webhook:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->delete_webhook: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The ID of the workspace | 
 **webhook_id** | **str**| The ID of the webhook | 

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
**200** | Deleted Webhook |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_webhook**
> WebhookResource get_webhook(workspace_id, webhook_id)

Get Webhook

Returns a webhook for the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.webhook_resource import WebhookResource
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
    api_instance = openapi_client.WebhooksApi(api_client)
    workspace_id = 'workspace_id_example' # str | The ID of the workspace
    webhook_id = 'webhook_id_example' # str | The ID of the webhook

    try:
        # Get Webhook
        api_response = api_instance.get_webhook(workspace_id, webhook_id)
        print("The response of WebhooksApi->get_webhook:\n")
        pprint(api_response)
    except Exception as e:
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

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Webhook |  -  |
**403** | Forbidden |  -  |
**404** | Not Found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_webhooks**
> ListWebhooks200Response list_webhooks(workspace_id)

List Webhooks

Retrieves a list of all webhooks for the requested workspace.

### Example

* Api Key Authentication (API Key with permissions):
```python
import time
import os
import openapi_client
from openapi_client.models.list_webhooks200_response import ListWebhooks200Response
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
    api_instance = openapi_client.WebhooksApi(api_client)
    workspace_id = 'workspace_id_example' # str | The ID of the workspace

    try:
        # List Webhooks
        api_response = api_instance.list_webhooks(workspace_id)
        print("The response of WebhooksApi->list_webhooks:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebhooksApi->list_webhooks: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workspace_id** | **str**| The ID of the workspace | 

### Return type

[**ListWebhooks200Response**](ListWebhooks200Response.md)

### Authorization

[API Key with permissions](../README.md#API Key with permissions)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of Webhooks |  -  |
**403** | Forbidden |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

