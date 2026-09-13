# CreateAssistantRequestTask


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**package_id** | **str** |  | 

## Example

```python
from robocorp.workspace.models.create_assistant_request_task import CreateAssistantRequestTask

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAssistantRequestTask from a JSON string
create_assistant_request_task_instance = CreateAssistantRequestTask.from_json(json)
# print the JSON string representation of the object
print CreateAssistantRequestTask.to_json()

# convert the object into a dict
create_assistant_request_task_dict = create_assistant_request_task_instance.to_dict()
# create an instance of CreateAssistantRequestTask from a dict
create_assistant_request_task_form_dict = create_assistant_request_task.from_dict(create_assistant_request_task_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


