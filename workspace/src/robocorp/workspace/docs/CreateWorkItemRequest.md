# CreateWorkItemRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**process** | [**AddWorkerToGroupRequestWorker**](AddWorkerToGroupRequestWorker.md) |  | 
**payload** | [**AnyValidJson**](AnyValidJson.md) |  | 

## Example

```python
from robocorp.workspace.models.create_work_item_request import CreateWorkItemRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateWorkItemRequest from a JSON string
create_work_item_request_instance = CreateWorkItemRequest.from_json(json)
# print the JSON string representation of the object
print CreateWorkItemRequest.to_json()

# convert the object into a dict
create_work_item_request_dict = create_work_item_request_instance.to_dict()
# create an instance of CreateWorkItemRequest from a dict
create_work_item_request_form_dict = create_work_item_request.from_dict(create_work_item_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


