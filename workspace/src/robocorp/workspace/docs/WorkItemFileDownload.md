# WorkItemFileDownload


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** | File download URL. The URL is valid for **one hour**. | 

## Example

```python
from robocorp.workspace.models.work_item_file_download import WorkItemFileDownload

# TODO update the JSON string below
json = "{}"
# create an instance of WorkItemFileDownload from a JSON string
work_item_file_download_instance = WorkItemFileDownload.from_json(json)
# print the JSON string representation of the object
print WorkItemFileDownload.to_json()

# convert the object into a dict
work_item_file_download_dict = work_item_file_download_instance.to_dict()
# create an instance of WorkItemFileDownload from a dict
work_item_file_download_form_dict = work_item_file_download.from_dict(work_item_file_download_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


