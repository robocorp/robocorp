# ListWebhooks200ResponseDataInner


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**process** | [**ListProcessRunWorkItems200ResponseDataInnerStepRun**](ListProcessRunWorkItems200ResponseDataInnerStepRun.md) |  | 
**enabled_events** | **List[str]** |  | 
**endpoint** | **str** |  | 

## Example

```python
from openapi_client.models.list_webhooks200_response_data_inner import ListWebhooks200ResponseDataInner

# TODO update the JSON string below
json = "{}"
# create an instance of ListWebhooks200ResponseDataInner from a JSON string
list_webhooks200_response_data_inner_instance = ListWebhooks200ResponseDataInner.from_json(json)
# print the JSON string representation of the object
print ListWebhooks200ResponseDataInner.to_json()

# convert the object into a dict
list_webhooks200_response_data_inner_dict = list_webhooks200_response_data_inner_instance.to_dict()
# create an instance of ListWebhooks200ResponseDataInner from a dict
list_webhooks200_response_data_inner_form_dict = list_webhooks200_response_data_inner.from_dict(list_webhooks200_response_data_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


