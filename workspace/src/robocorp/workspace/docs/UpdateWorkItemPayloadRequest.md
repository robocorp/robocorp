# UpdateWorkItemPayloadRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**payload** | [**AnyValidJson**](AnyValidJson.md) |  | 

## Example

```python
from robocorp.workspace.models.update_work_item_payload_request import UpdateWorkItemPayloadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateWorkItemPayloadRequest from a JSON string
update_work_item_payload_request_instance = UpdateWorkItemPayloadRequest.from_json(json)
# print the JSON string representation of the object
print UpdateWorkItemPayloadRequest.to_json()

# convert the object into a dict
update_work_item_payload_request_dict = update_work_item_payload_request_instance.to_dict()
# create an instance of UpdateWorkItemPayloadRequest from a dict
update_work_item_payload_request_form_dict = update_work_item_payload_request.from_dict(update_work_item_payload_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


