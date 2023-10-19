# ProcessWebhookPayload


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**endpoint** | **str** |  | 
**enabled_events** | **List[str]** |  | 
**process** | [**AddWorkerToGroupRequestWorker**](AddWorkerToGroupRequestWorker.md) |  | 

## Example

```python
from workspace.models.process_webhook_payload import ProcessWebhookPayload

# TODO update the JSON string below
json = "{}"
# create an instance of ProcessWebhookPayload from a JSON string
process_webhook_payload_instance = ProcessWebhookPayload.from_json(json)
# print the JSON string representation of the object
print ProcessWebhookPayload.to_json()

# convert the object into a dict
process_webhook_payload_dict = process_webhook_payload_instance.to_dict()
# create an instance of ProcessWebhookPayload from a dict
process_webhook_payload_form_dict = process_webhook_payload.from_dict(process_webhook_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


