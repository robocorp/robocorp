# ProcessRunResourceStartedBy


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**details** | [**ProcessRunResourceStartedByDetails**](ProcessRunResourceStartedByDetails.md) |  | 

## Example

```python
from workspace.models.process_run_resource_started_by import ProcessRunResourceStartedBy

# TODO update the JSON string below
json = "{}"
# create an instance of ProcessRunResourceStartedBy from a JSON string
process_run_resource_started_by_instance = ProcessRunResourceStartedBy.from_json(json)
# print the JSON string representation of the object
print ProcessRunResourceStartedBy.to_json()

# convert the object into a dict
process_run_resource_started_by_dict = process_run_resource_started_by_instance.to_dict()
# create an instance of ProcessRunResourceStartedBy from a dict
process_run_resource_started_by_form_dict = process_run_resource_started_by.from_dict(process_run_resource_started_by_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


