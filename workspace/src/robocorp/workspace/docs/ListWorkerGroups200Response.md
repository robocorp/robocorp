# ListWorkerGroups200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next** | [**pydantic.StrictStr**](Next.md) |  | 
**has_more** | [**pydantic.StrictBool**](HasMore.md) |  | 
**data** | [**List[WorkerGroupResource]**](WorkerGroupResource.md) |  | 

## Example

```python
from robocorp.workspace.models.list_worker_groups200_response import ListWorkerGroups200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListWorkerGroups200Response from a JSON string
list_worker_groups200_response_instance = ListWorkerGroups200Response.from_json(json)
# print the JSON string representation of the object
print ListWorkerGroups200Response.to_json()

# convert the object into a dict
list_worker_groups200_response_dict = list_worker_groups200_response_instance.to_dict()
# create an instance of ListWorkerGroups200Response from a dict
list_worker_groups200_response_form_dict = list_worker_groups200_response.from_dict(list_worker_groups200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


