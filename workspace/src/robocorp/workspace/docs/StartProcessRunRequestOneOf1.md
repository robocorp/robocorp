# StartProcessRunRequestOneOf1


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**work_item_ids** | **List[str]** | Work item ids to start the run with. | 
**callback** | [**ProcessRunCallback**](ProcessRunCallback.md) |  | [optional] 

## Example

```python
from robocorp.workspace.models.start_process_run_request_one_of1 import StartProcessRunRequestOneOf1

# TODO update the JSON string below
json = "{}"
# create an instance of StartProcessRunRequestOneOf1 from a JSON string
start_process_run_request_one_of1_instance = StartProcessRunRequestOneOf1.from_json(json)
# print the JSON string representation of the object
print StartProcessRunRequestOneOf1.to_json()

# convert the object into a dict
start_process_run_request_one_of1_dict = start_process_run_request_one_of1_instance.to_dict()
# create an instance of StartProcessRunRequestOneOf1 from a dict
start_process_run_request_one_of1_form_dict = start_process_run_request_one_of1.from_dict(start_process_run_request_one_of1_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


