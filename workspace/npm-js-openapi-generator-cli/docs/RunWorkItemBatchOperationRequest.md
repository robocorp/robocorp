# RunWorkItemBatchOperationRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**batch_operation** | **str** |  | 
**work_item_ids** | **List[str]** |  | 

## Example

```python
from openapi_client.models.run_work_item_batch_operation_request import RunWorkItemBatchOperationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of RunWorkItemBatchOperationRequest from a JSON string
run_work_item_batch_operation_request_instance = RunWorkItemBatchOperationRequest.from_json(json)
# print the JSON string representation of the object
print RunWorkItemBatchOperationRequest.to_json()

# convert the object into a dict
run_work_item_batch_operation_request_dict = run_work_item_batch_operation_request_instance.to_dict()
# create an instance of RunWorkItemBatchOperationRequest from a dict
run_work_item_batch_operation_request_form_dict = run_work_item_batch_operation_request.from_dict(run_work_item_batch_operation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


