# StartProcessRunRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**callback** | [**ProcessRunCallback**](ProcessRunCallback.md) |  | [optional] 
**type** | **str** |  | 
**work_item_ids** | **List[str]** | Work item ids to start the run with. | 
**payloads** | [**List[AnyValidJson]**](AnyValidJson.md) |  | 

## Example

```python
from robocorp.workspace.models.start_process_run_request import StartProcessRunRequest

# TODO update the JSON string below
json = "{}"
# create an instance of StartProcessRunRequest from a JSON string
start_process_run_request_instance = StartProcessRunRequest.from_json(json)
# print the JSON string representation of the object
print StartProcessRunRequest.to_json()

# convert the object into a dict
start_process_run_request_dict = start_process_run_request_instance.to_dict()
# create an instance of StartProcessRunRequest from a dict
start_process_run_request_form_dict = start_process_run_request.from_dict(start_process_run_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


