# WorkerGroupResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 

## Example

```python
from robocorp.workspace.models.worker_group_resource import WorkerGroupResource

# TODO update the JSON string below
json = "{}"
# create an instance of WorkerGroupResource from a JSON string
worker_group_resource_instance = WorkerGroupResource.from_json(json)
# print the JSON string representation of the object
print WorkerGroupResource.to_json()

# convert the object into a dict
worker_group_resource_dict = worker_group_resource_instance.to_dict()
# create an instance of WorkerGroupResource from a dict
worker_group_resource_form_dict = worker_group_resource.from_dict(worker_group_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


