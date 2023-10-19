# StartProcessRunRequestOneOf3


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**payloads** | [**List[AnyValidJson]**](AnyValidJson.md) |  | 
**callback** | [**ProcessRunCallback**](ProcessRunCallback.md) |  | [optional] 

## Example

```python
from workspace.models.start_process_run_request_one_of3 import StartProcessRunRequestOneOf3

# TODO update the JSON string below
json = "{}"
# create an instance of StartProcessRunRequestOneOf3 from a JSON string
start_process_run_request_one_of3_instance = StartProcessRunRequestOneOf3.from_json(json)
# print the JSON string representation of the object
print StartProcessRunRequestOneOf3.to_json()

# convert the object into a dict
start_process_run_request_one_of3_dict = start_process_run_request_one_of3_instance.to_dict()
# create an instance of StartProcessRunRequestOneOf3 from a dict
start_process_run_request_one_of3_form_dict = start_process_run_request_one_of3.from_dict(start_process_run_request_one_of3_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


