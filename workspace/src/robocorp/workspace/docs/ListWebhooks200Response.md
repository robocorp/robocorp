# ListWebhooks200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[ListWebhooks200ResponseDataInner]**](ListWebhooks200ResponseDataInner.md) |  | 

## Example

```python
from workspace.models.list_webhooks200_response import ListWebhooks200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListWebhooks200Response from a JSON string
list_webhooks200_response_instance = ListWebhooks200Response.from_json(json)
# print the JSON string representation of the object
print ListWebhooks200Response.to_json()

# convert the object into a dict
list_webhooks200_response_dict = list_webhooks200_response_instance.to_dict()
# create an instance of ListWebhooks200Response from a dict
list_webhooks200_response_form_dict = list_webhooks200_response.from_dict(list_webhooks200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


