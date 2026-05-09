# ListStepRunArtifacts200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[ListStepRunArtifacts200ResponseDataInner]**](ListStepRunArtifacts200ResponseDataInner.md) |  | 

## Example

```python
from openapi_client.models.list_step_run_artifacts200_response import ListStepRunArtifacts200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListStepRunArtifacts200Response from a JSON string
list_step_run_artifacts200_response_instance = ListStepRunArtifacts200Response.from_json(json)
# print the JSON string representation of the object
print ListStepRunArtifacts200Response.to_json()

# convert the object into a dict
list_step_run_artifacts200_response_dict = list_step_run_artifacts200_response_instance.to_dict()
# create an instance of ListStepRunArtifacts200Response from a dict
list_step_run_artifacts200_response_form_dict = list_step_run_artifacts200_response.from_dict(list_step_run_artifacts200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


