# AssetUploadPendingResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**status** | **str** |  | 
**content_type** | **str** |  | 

## Example

```python
from openapi_client.models.asset_upload_pending_resource import AssetUploadPendingResource

# TODO update the JSON string below
json = "{}"
# create an instance of AssetUploadPendingResource from a JSON string
asset_upload_pending_resource_instance = AssetUploadPendingResource.from_json(json)
# print the JSON string representation of the object
print AssetUploadPendingResource.to_json()

# convert the object into a dict
asset_upload_pending_resource_dict = asset_upload_pending_resource_instance.to_dict()
# create an instance of AssetUploadPendingResource from a dict
asset_upload_pending_resource_form_dict = asset_upload_pending_resource.from_dict(asset_upload_pending_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


