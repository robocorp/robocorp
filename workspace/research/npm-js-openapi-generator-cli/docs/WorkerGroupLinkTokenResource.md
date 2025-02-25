# WorkerGroupLinkTokenResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**expires_at** | **datetime** |  | 
**worker_group** | [**AddWorkerToGroupRequestWorker**](AddWorkerToGroupRequestWorker.md) |  | 

## Example

```python
from openapi_client.models.worker_group_link_token_resource import WorkerGroupLinkTokenResource

# TODO update the JSON string below
json = "{}"
# create an instance of WorkerGroupLinkTokenResource from a JSON string
worker_group_link_token_resource_instance = WorkerGroupLinkTokenResource.from_json(json)
# print the JSON string representation of the object
print WorkerGroupLinkTokenResource.to_json()

# convert the object into a dict
worker_group_link_token_resource_dict = worker_group_link_token_resource_instance.to_dict()
# create an instance of WorkerGroupLinkTokenResource from a dict
worker_group_link_token_resource_form_dict = worker_group_link_token_resource.from_dict(worker_group_link_token_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


