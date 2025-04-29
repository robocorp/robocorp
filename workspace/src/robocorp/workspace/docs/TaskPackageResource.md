# TaskPackageResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**type** | **str** |  | 
**tasks** | [**List[UpdateWorkerRequest]**](UpdateWorkerRequest.md) | Tasks contained in the task package: empty array if the task package has not been uploaded yet. | 
**download** | [**TaskPackageResourceDownload**](TaskPackageResourceDownload.md) |  | 

## Example

```python
from robocorp.workspace.models.task_package_resource import TaskPackageResource

# TODO update the JSON string below
json = "{}"
# create an instance of TaskPackageResource from a JSON string
task_package_resource_instance = TaskPackageResource.from_json(json)
# print the JSON string representation of the object
print TaskPackageResource.to_json()

# convert the object into a dict
task_package_resource_dict = task_package_resource_instance.to_dict()
# create an instance of TaskPackageResource from a dict
task_package_resource_form_dict = task_package_resource.from_dict(task_package_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


