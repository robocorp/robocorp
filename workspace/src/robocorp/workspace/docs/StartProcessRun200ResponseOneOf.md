# StartProcessRun200ResponseOneOf

This signals that a new process run was not started. This happens when a process run start with Input Work Items is requested, but no Input Work Items are available. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**started** | **bool** |  | 

## Example

```python
from robocorp.workspace.models.start_process_run200_response_one_of import StartProcessRun200ResponseOneOf

# TODO update the JSON string below
json = "{}"
# create an instance of StartProcessRun200ResponseOneOf from a JSON string
start_process_run200_response_one_of_instance = StartProcessRun200ResponseOneOf.from_json(json)
# print the JSON string representation of the object
print StartProcessRun200ResponseOneOf.to_json()

# convert the object into a dict
start_process_run200_response_one_of_dict = start_process_run200_response_one_of_instance.to_dict()
# create an instance of StartProcessRun200ResponseOneOf from a dict
start_process_run200_response_one_of_form_dict = start_process_run200_response_one_of.from_dict(start_process_run200_response_one_of_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


