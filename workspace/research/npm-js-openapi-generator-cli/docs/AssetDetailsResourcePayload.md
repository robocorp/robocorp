# AssetDetailsResourcePayload


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**content_type** | **str** |  | 
**url** | **str** |  | 

## Example

```python
from openapi_client.models.asset_details_resource_payload import AssetDetailsResourcePayload

# TODO update the JSON string below
json = "{}"
# create an instance of AssetDetailsResourcePayload from a JSON string
asset_details_resource_payload_instance = AssetDetailsResourcePayload.from_json(json)
# print the JSON string representation of the object
print AssetDetailsResourcePayload.to_json()

# convert the object into a dict
asset_details_resource_payload_dict = asset_details_resource_payload_instance.to_dict()
# create an instance of AssetDetailsResourcePayload from a dict
asset_details_resource_payload_form_dict = asset_details_resource_payload.from_dict(asset_details_resource_payload_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


