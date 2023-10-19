# AssistantRunResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**state** | **str** |  | 
**error** | [**AssistantRunResourceError**](AssistantRunResourceError.md) |  | 
**started_at** | **datetime** |  | 
**ended_at** | **datetime** |  | 
**duration** | **float** |  | 
**assistant** | [**ListAssets200ResponseDataInner**](ListAssets200ResponseDataInner.md) |  | 

## Example

```python
from workspace.models.assistant_run_resource import AssistantRunResource

# TODO update the JSON string below
json = "{}"
# create an instance of AssistantRunResource from a JSON string
assistant_run_resource_instance = AssistantRunResource.from_json(json)
# print the JSON string representation of the object
print AssistantRunResource.to_json()

# convert the object into a dict
assistant_run_resource_dict = assistant_run_resource_instance.to_dict()
# create an instance of AssistantRunResource from a dict
assistant_run_resource_form_dict = assistant_run_resource.from_dict(assistant_run_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


