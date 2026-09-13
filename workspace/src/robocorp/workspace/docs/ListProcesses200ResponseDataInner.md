# ListProcesses200ResponseDataInner


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**created_at** | **datetime** |  | 

## Example

```python
from robocorp.workspace.models.list_processes200_response_data_inner import ListProcesses200ResponseDataInner

# TODO update the JSON string below
json = "{}"
# create an instance of ListProcesses200ResponseDataInner from a JSON string
list_processes200_response_data_inner_instance = ListProcesses200ResponseDataInner.from_json(json)
# print the JSON string representation of the object
print ListProcesses200ResponseDataInner.to_json()

# convert the object into a dict
list_processes200_response_data_inner_dict = list_processes200_response_data_inner_instance.to_dict()
# create an instance of ListProcesses200ResponseDataInner from a dict
list_processes200_response_data_inner_form_dict = list_processes200_response_data_inner.from_dict(list_processes200_response_data_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


