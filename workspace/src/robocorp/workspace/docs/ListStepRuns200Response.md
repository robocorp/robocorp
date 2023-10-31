# ListStepRuns200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next** | [**pydantic.StrictStr**](Next.md) |  | 
**has_more** | [**pydantic.StrictBool**](HasMore.md) |  | 
**data** | [**List[StepRunResource]**](StepRunResource.md) |  | 

## Example

```python
from robocorp.workspace.models.list_step_runs200_response import ListStepRuns200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListStepRuns200Response from a JSON string
list_step_runs200_response_instance = ListStepRuns200Response.from_json(json)
# print the JSON string representation of the object
print ListStepRuns200Response.to_json()

# convert the object into a dict
list_step_runs200_response_dict = list_step_runs200_response_instance.to_dict()
# create an instance of ListStepRuns200Response from a dict
list_step_runs200_response_form_dict = list_step_runs200_response.from_dict(list_step_runs200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


