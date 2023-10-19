# StepRunResourceError

An object containing the error code, if the run failed.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** |  | 

## Example

```python
from workspace.models.step_run_resource_error import StepRunResourceError

# TODO update the JSON string below
json = "{}"
# create an instance of StepRunResourceError from a JSON string
step_run_resource_error_instance = StepRunResourceError.from_json(json)
# print the JSON string representation of the object
print StepRunResourceError.to_json()

# convert the object into a dict
step_run_resource_error_dict = step_run_resource_error_instance.to_dict()
# create an instance of StepRunResourceError from a dict
step_run_resource_error_form_dict = step_run_resource_error.from_dict(step_run_resource_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


