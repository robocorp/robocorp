# GetAssistant200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**task** | [**CreateAssistantRequestTask**](CreateAssistantRequestTask.md) |  | 
**created_at** | **datetime** |  | 

## Example

```python
from openapi_client.models.get_assistant200_response import GetAssistant200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetAssistant200Response from a JSON string
get_assistant200_response_instance = GetAssistant200Response.from_json(json)
# print the JSON string representation of the object
print GetAssistant200Response.to_json()

# convert the object into a dict
get_assistant200_response_dict = get_assistant200_response_instance.to_dict()
# create an instance of GetAssistant200Response from a dict
get_assistant200_response_form_dict = get_assistant200_response.from_dict(get_assistant200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


