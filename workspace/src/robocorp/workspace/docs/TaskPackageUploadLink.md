# TaskPackageUploadLink


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** |  | 
**form_data** | **object** | The form data fields you must include when uploading the task package bundle | 

## Example

```python
from workspace.models.task_package_upload_link import TaskPackageUploadLink

# TODO update the JSON string below
json = "{}"
# create an instance of TaskPackageUploadLink from a JSON string
task_package_upload_link_instance = TaskPackageUploadLink.from_json(json)
# print the JSON string representation of the object
print TaskPackageUploadLink.to_json()

# convert the object into a dict
task_package_upload_link_dict = task_package_upload_link_instance.to_dict()
# create an instance of TaskPackageUploadLink from a dict
task_package_upload_link_form_dict = task_package_upload_link.from_dict(task_package_upload_link_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


