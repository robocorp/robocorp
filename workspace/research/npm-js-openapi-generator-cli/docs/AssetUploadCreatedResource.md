# AssetUploadCreatedResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**status** | **str** |  | 
**content_type** | **str** |  | 

## Example

```python
from openapi_client.models.asset_upload_created_resource import AssetUploadCreatedResource

# TODO update the JSON string below
json = "{}"
# create an instance of AssetUploadCreatedResource from a JSON string
asset_upload_created_resource_instance = AssetUploadCreatedResource.from_json(json)
# print the JSON string representation of the object
print AssetUploadCreatedResource.to_json()

# convert the object into a dict
asset_upload_created_resource_dict = asset_upload_created_resource_instance.to_dict()
# create an instance of AssetUploadCreatedResource from a dict
asset_upload_created_resource_form_dict = asset_upload_created_resource.from_dict(asset_upload_created_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


