# WorkItemWithoutDataResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**created_at** | **datetime** |  | 
**state** | [**WorkItemState**](WorkItemState.md) |  | 
**state_updated_at** | **datetime** |  | 
**process** | [**AddWorkerToGroupRequestWorker**](AddWorkerToGroupRequestWorker.md) |  | 
**process_run** | [**ListProcessRunWorkItems200ResponseDataInnerStepRun**](ListProcessRunWorkItems200ResponseDataInnerStepRun.md) |  | 
**step** | [**ListProcessRunWorkItems200ResponseDataInnerStepRun**](ListProcessRunWorkItems200ResponseDataInnerStepRun.md) |  | 
**step_run** | [**ListProcessRunWorkItems200ResponseDataInnerStepRun**](ListProcessRunWorkItems200ResponseDataInnerStepRun.md) |  | 
**exception** | [**WorkItemException**](WorkItemException.md) |  | 

## Example

```python
from openapi_client.models.work_item_without_data_resource import WorkItemWithoutDataResource

# TODO update the JSON string below
json = "{}"
# create an instance of WorkItemWithoutDataResource from a JSON string
work_item_without_data_resource_instance = WorkItemWithoutDataResource.from_json(json)
# print the JSON string representation of the object
print WorkItemWithoutDataResource.to_json()

# convert the object into a dict
work_item_without_data_resource_dict = work_item_without_data_resource_instance.to_dict()
# create an instance of WorkItemWithoutDataResource from a dict
work_item_without_data_resource_form_dict = work_item_without_data_resource.from_dict(work_item_without_data_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


