# GetStepRunArtifact200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**size** | **float** |  | 
**url** | **str** |  | 

## Example

```python
from workspace.models.get_step_run_artifact200_response import GetStepRunArtifact200Response

# TODO update the JSON string below
json = "{}"
# create an instance of GetStepRunArtifact200Response from a JSON string
get_step_run_artifact200_response_instance = GetStepRunArtifact200Response.from_json(json)
# print the JSON string representation of the object
print GetStepRunArtifact200Response.to_json()

# convert the object into a dict
get_step_run_artifact200_response_dict = get_step_run_artifact200_response_instance.to_dict()
# create an instance of GetStepRunArtifact200Response from a dict
get_step_run_artifact200_response_form_dict = get_step_run_artifact200_response.from_dict(get_step_run_artifact200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


