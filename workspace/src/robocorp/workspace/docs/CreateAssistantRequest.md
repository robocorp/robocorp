# CreateAssistantRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**task** | [**CreateAssistantRequestTask**](CreateAssistantRequestTask.md) |  | 

## Example

```python
from workspace.models.create_assistant_request import CreateAssistantRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAssistantRequest from a JSON string
create_assistant_request_instance = CreateAssistantRequest.from_json(json)
# print the JSON string representation of the object
print CreateAssistantRequest.to_json()

# convert the object into a dict
create_assistant_request_dict = create_assistant_request_instance.to_dict()
# create an instance of CreateAssistantRequest from a dict
create_assistant_request_form_dict = create_assistant_request.from_dict(create_assistant_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


