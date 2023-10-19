# ListWorkItems200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next** | [**Next**](Next.md) |  | 
**has_more** | [**HasMore**](HasMore.md) |  | 
**data** | [**List[WorkItemWithoutDataResource]**](WorkItemWithoutDataResource.md) |  | 

## Example

```python
from workspace.models.list_work_items200_response import ListWorkItems200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListWorkItems200Response from a JSON string
list_work_items200_response_instance = ListWorkItems200Response.from_json(json)
# print the JSON string representation of the object
print ListWorkItems200Response.to_json()

# convert the object into a dict
list_work_items200_response_dict = list_work_items200_response_instance.to_dict()
# create an instance of ListWorkItems200Response from a dict
list_work_items200_response_form_dict = list_work_items200_response.from_dict(list_work_items200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


