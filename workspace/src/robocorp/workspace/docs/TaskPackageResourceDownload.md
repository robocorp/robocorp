# TaskPackageResourceDownload


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** | The URL to download the task package. Null if the task package has not been uploaded yet. | 

## Example

```python
from robocorp.workspace.models.task_package_resource_download import TaskPackageResourceDownload

# TODO update the JSON string below
json = "{}"
# create an instance of TaskPackageResourceDownload from a JSON string
task_package_resource_download_instance = TaskPackageResourceDownload.from_json(json)
# print the JSON string representation of the object
print TaskPackageResourceDownload.to_json()

# convert the object into a dict
task_package_resource_download_dict = task_package_resource_download_instance.to_dict()
# create an instance of TaskPackageResourceDownload from a dict
task_package_resource_download_form_dict = task_package_resource_download.from_dict(task_package_resource_download_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


