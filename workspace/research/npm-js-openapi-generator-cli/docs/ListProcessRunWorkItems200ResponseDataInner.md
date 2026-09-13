# ListProcessRunWorkItems200ResponseDataInner


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**created_at** | **datetime** |  | 
**state** | **str** |  | 
**state_updated_at** | **datetime** |  | 
**process** | [**AddWorkerToGroupRequestWorker**](AddWorkerToGroupRequestWorker.md) |  | 
**process_run** | [**AddWorkerToGroupRequestWorker**](AddWorkerToGroupRequestWorker.md) |  | 
**step** | [**AddWorkerToGroupRequestWorker**](AddWorkerToGroupRequestWorker.md) |  | 
**step_run** | [**ListProcessRunWorkItems200ResponseDataInnerStepRun**](ListProcessRunWorkItems200ResponseDataInnerStepRun.md) |  | 
**exception** | [**WorkItemException**](WorkItemException.md) |  | 

## Example

```python
from openapi_client.models.list_process_run_work_items200_response_data_inner import ListProcessRunWorkItems200ResponseDataInner

# TODO update the JSON string below
json = "{}"
# create an instance of ListProcessRunWorkItems200ResponseDataInner from a JSON string
list_process_run_work_items200_response_data_inner_instance = ListProcessRunWorkItems200ResponseDataInner.from_json(json)
# print the JSON string representation of the object
print ListProcessRunWorkItems200ResponseDataInner.to_json()

# convert the object into a dict
list_process_run_work_items200_response_data_inner_dict = list_process_run_work_items200_response_data_inner_instance.to_dict()
# create an instance of ListProcessRunWorkItems200ResponseDataInner from a dict
list_process_run_work_items200_response_data_inner_form_dict = list_process_run_work_items200_response_data_inner.from_dict(list_process_run_work_items200_response_data_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


