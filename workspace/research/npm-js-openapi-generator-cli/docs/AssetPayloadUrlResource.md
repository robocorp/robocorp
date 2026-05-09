# AssetPayloadUrlResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**content_type** | **str** |  | 
**url** | **str** |  | 

## Example

```python
from openapi_client.models.asset_payload_url_resource import AssetPayloadUrlResource

# TODO update the JSON string below
json = "{}"
# create an instance of AssetPayloadUrlResource from a JSON string
asset_payload_url_resource_instance = AssetPayloadUrlResource.from_json(json)
# print the JSON string representation of the object
print AssetPayloadUrlResource.to_json()

# convert the object into a dict
asset_payload_url_resource_dict = asset_payload_url_resource_instance.to_dict()
# create an instance of AssetPayloadUrlResource from a dict
asset_payload_url_resource_form_dict = asset_payload_url_resource.from_dict(asset_payload_url_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


