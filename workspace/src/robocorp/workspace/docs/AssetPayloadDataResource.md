# AssetPayloadDataResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**type** | **str** |  | 
**content_type** | **str** |  | 
**data** | **str** |  | 

## Example

```python
from robocorp.workspace.models.asset_payload_data_resource import AssetPayloadDataResource

# TODO update the JSON string below
json = "{}"
# create an instance of AssetPayloadDataResource from a JSON string
asset_payload_data_resource_instance = AssetPayloadDataResource.from_json(json)
# print the JSON string representation of the object
print AssetPayloadDataResource.to_json()

# convert the object into a dict
asset_payload_data_resource_dict = asset_payload_data_resource_instance.to_dict()
# create an instance of AssetPayloadDataResource from a dict
asset_payload_data_resource_form_dict = asset_payload_data_resource.from_dict(asset_payload_data_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


