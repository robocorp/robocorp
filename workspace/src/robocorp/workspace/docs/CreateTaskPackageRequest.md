# CreateTaskPackageRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**type** | **str** |  | 

## Example

```python
from robocorp.workspace.models.create_task_package_request import CreateTaskPackageRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateTaskPackageRequest from a JSON string
create_task_package_request_instance = CreateTaskPackageRequest.from_json(json)
# print the JSON string representation of the object
print CreateTaskPackageRequest.to_json()

# convert the object into a dict
create_task_package_request_dict = create_task_package_request_instance.to_dict()
# create an instance of CreateTaskPackageRequest from a dict
create_task_package_request_form_dict = create_task_package_request.from_dict(create_task_package_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


