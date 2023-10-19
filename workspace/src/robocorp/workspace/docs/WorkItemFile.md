# WorkItemFile


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**size** | **float** | File size in bytes | 
**name** | **str** | File name | 

## Example

```python
from workspace.models.work_item_file import WorkItemFile

# TODO update the JSON string below
json = "{}"
# create an instance of WorkItemFile from a JSON string
work_item_file_instance = WorkItemFile.from_json(json)
# print the JSON string representation of the object
print WorkItemFile.to_json()

# convert the object into a dict
work_item_file_dict = work_item_file_instance.to_dict()
# create an instance of WorkItemFile from a dict
work_item_file_form_dict = work_item_file.from_dict(work_item_file_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


