# ListWorkspaceProcessRuns200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next** | [**Next**](Next.md) |  | 
**has_more** | [**HasMore**](HasMore.md) |  | 
**data** | [**List[ProcessRunResource]**](ProcessRunResource.md) |  | 

## Example

```python
from openapi_client.models.list_workspace_process_runs200_response import ListWorkspaceProcessRuns200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListWorkspaceProcessRuns200Response from a JSON string
list_workspace_process_runs200_response_instance = ListWorkspaceProcessRuns200Response.from_json(json)
# print the JSON string representation of the object
print ListWorkspaceProcessRuns200Response.to_json()

# convert the object into a dict
list_workspace_process_runs200_response_dict = list_workspace_process_runs200_response_instance.to_dict()
# create an instance of ListWorkspaceProcessRuns200Response from a dict
list_workspace_process_runs200_response_form_dict = list_workspace_process_runs200_response.from_dict(list_workspace_process_runs200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


