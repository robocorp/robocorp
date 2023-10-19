# AssetUploadCreatedResourceWithUrl


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**status** | **str** |  | 
**content_type** | **str** |  | 
**upload_url** | **str** |  | 

## Example

```python
from workspace.models.asset_upload_created_resource_with_url import AssetUploadCreatedResourceWithUrl

# TODO update the JSON string below
json = "{}"
# create an instance of AssetUploadCreatedResourceWithUrl from a JSON string
asset_upload_created_resource_with_url_instance = AssetUploadCreatedResourceWithUrl.from_json(json)
# print the JSON string representation of the object
print AssetUploadCreatedResourceWithUrl.to_json()

# convert the object into a dict
asset_upload_created_resource_with_url_dict = asset_upload_created_resource_with_url_instance.to_dict()
# create an instance of AssetUploadCreatedResourceWithUrl from a dict
asset_upload_created_resource_with_url_form_dict = asset_upload_created_resource_with_url.from_dict(asset_upload_created_resource_with_url_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


