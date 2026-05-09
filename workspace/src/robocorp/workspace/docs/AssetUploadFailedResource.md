# AssetUploadFailedResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**status** | **str** |  | 
**content_type** | **str** |  | 
**reason** | **str** |  | 

## Example

```python
from robocorp.workspace.models.asset_upload_failed_resource import AssetUploadFailedResource

# TODO update the JSON string below
json = "{}"
# create an instance of AssetUploadFailedResource from a JSON string
asset_upload_failed_resource_instance = AssetUploadFailedResource.from_json(json)
# print the JSON string representation of the object
print AssetUploadFailedResource.to_json()

# convert the object into a dict
asset_upload_failed_resource_dict = asset_upload_failed_resource_instance.to_dict()
# create an instance of AssetUploadFailedResource from a dict
asset_upload_failed_resource_form_dict = asset_upload_failed_resource.from_dict(asset_upload_failed_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


