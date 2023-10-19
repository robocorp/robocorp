# AssistantResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**task** | [**AssistantResourceTask**](AssistantResourceTask.md) |  | 
**created_at** | **datetime** |  | 

## Example

```python
from workspace.models.assistant_resource import AssistantResource

# TODO update the JSON string below
json = "{}"
# create an instance of AssistantResource from a JSON string
assistant_resource_instance = AssistantResource.from_json(json)
# print the JSON string representation of the object
print AssistantResource.to_json()

# convert the object into a dict
assistant_resource_dict = assistant_resource_instance.to_dict()
# create an instance of AssistantResource from a dict
assistant_resource_form_dict = assistant_resource.from_dict(assistant_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


