# StepRunResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**state** | **str** |  | 
**state_updated_at** | **datetime** |  | 
**error** | [**StepRunResourceError**](StepRunResourceError.md) |  | 
**started_at** | **datetime** |  | 
**ended_at** | **datetime** |  | 
**duration** | **float** |  | 
**step** | [**ListAssets200ResponseDataInner**](ListAssets200ResponseDataInner.md) |  | 

## Example

```python
from robocorp.workspace.models.step_run_resource import StepRunResource

# TODO update the JSON string below
json = "{}"
# create an instance of StepRunResource from a JSON string
step_run_resource_instance = StepRunResource.from_json(json)
# print the JSON string representation of the object
print StepRunResource.to_json()

# convert the object into a dict
step_run_resource_dict = step_run_resource_instance.to_dict()
# create an instance of StepRunResource from a dict
step_run_resource_form_dict = step_run_resource.from_dict(step_run_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


