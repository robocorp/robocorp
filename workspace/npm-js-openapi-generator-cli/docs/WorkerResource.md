# WorkerResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**state** | **str** |  | 

## Example

```python
from openapi_client.models.worker_resource import WorkerResource

# TODO update the JSON string below
json = "{}"
# create an instance of WorkerResource from a JSON string
worker_resource_instance = WorkerResource.from_json(json)
# print the JSON string representation of the object
print WorkerResource.to_json()

# convert the object into a dict
worker_resource_dict = worker_resource_instance.to_dict()
# create an instance of WorkerResource from a dict
worker_resource_form_dict = worker_resource.from_dict(worker_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


