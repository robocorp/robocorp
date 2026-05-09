# WorkItemResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**created_at** | **datetime** |  | 
**state** | [**WorkItemState**](WorkItemState.md) |  | 
**state_updated_at** | **datetime** |  | 
**process** | [**AddWorkerToGroupRequestWorker**](AddWorkerToGroupRequestWorker.md) |  | 
**process_run** | [**ListWebhooks200ResponseDataInnerProcess**](ListWebhooks200ResponseDataInnerProcess.md) |  | 
**step** | [**ListWebhooks200ResponseDataInnerProcess**](ListWebhooks200ResponseDataInnerProcess.md) |  | 
**step_run** | [**ListWebhooks200ResponseDataInnerProcess**](ListWebhooks200ResponseDataInnerProcess.md) |  | 
**payload** | [**AnyValidJson**](AnyValidJson.md) |  | 
**files** | [**List[WorkItemFile]**](WorkItemFile.md) |  | 
**exception** | [**WorkItemException**](WorkItemException.md) |  | 

## Example

```python
from robocorp.workspace.models.work_item_resource import WorkItemResource

# TODO update the JSON string below
json = "{}"
# create an instance of WorkItemResource from a JSON string
work_item_resource_instance = WorkItemResource.from_json(json)
# print the JSON string representation of the object
print WorkItemResource.to_json()

# convert the object into a dict
work_item_resource_dict = work_item_resource_instance.to_dict()
# create an instance of WorkItemResource from a dict
work_item_resource_form_dict = work_item_resource.from_dict(work_item_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


