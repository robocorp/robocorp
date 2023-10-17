# StopProcessRunRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**set_remaining_work_items_as_done** | **bool** |  | 
**terminate_ongoing_activity_runs** | **bool** |  | 
**reason** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.stop_process_run_request import StopProcessRunRequest

# TODO update the JSON string below
json = "{}"
# create an instance of StopProcessRunRequest from a JSON string
stop_process_run_request_instance = StopProcessRunRequest.from_json(json)
# print the JSON string representation of the object
print StopProcessRunRequest.to_json()

# convert the object into a dict
stop_process_run_request_dict = stop_process_run_request_instance.to_dict()
# create an instance of StopProcessRunRequest from a dict
stop_process_run_request_form_dict = stop_process_run_request.from_dict(stop_process_run_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


