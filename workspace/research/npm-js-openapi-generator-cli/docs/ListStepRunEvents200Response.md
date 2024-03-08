# ListStepRunEvents200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[ListStepRunEvents200ResponseDataInner]**](ListStepRunEvents200ResponseDataInner.md) |  | 

## Example

```python
from openapi_client.models.list_step_run_events200_response import ListStepRunEvents200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListStepRunEvents200Response from a JSON string
list_step_run_events200_response_instance = ListStepRunEvents200Response.from_json(json)
# print the JSON string representation of the object
print ListStepRunEvents200Response.to_json()

# convert the object into a dict
list_step_run_events200_response_dict = list_step_run_events200_response_instance.to_dict()
# create an instance of ListStepRunEvents200Response from a dict
list_step_run_events200_response_form_dict = list_step_run_events200_response.from_dict(list_step_run_events200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


