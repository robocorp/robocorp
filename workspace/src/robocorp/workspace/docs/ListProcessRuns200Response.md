# ListProcessRuns200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next** | [**Optional[StrictStr]**](Next.md) |  | 
**has_more** | [**StrictBool**](HasMore.md) |  | 
**data** | [**List[ProcessRunResource]**](ProcessRunResource.md) |  | 

## Example

```python
from robocorp.workspace.models.list_process_runs200_response import ListProcessRuns200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListProcessRuns200Response from a JSON string
list_process_runs200_response_instance = ListProcessRuns200Response.from_json(json)
# print the JSON string representation of the object
print ListProcessRuns200Response.to_json()

# convert the object into a dict
list_process_runs200_response_dict = list_process_runs200_response_instance.to_dict()
# create an instance of ListProcessRuns200Response from a dict
list_process_runs200_response_form_dict = list_process_runs200_response.from_dict(list_process_runs200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


