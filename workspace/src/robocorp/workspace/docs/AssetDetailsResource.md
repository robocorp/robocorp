# AssetDetailsResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**payload** | [**AssetDetailsResourcePayload**](AssetDetailsResourcePayload.md) |  | 

## Example

```python
from robocorp.workspace.models.asset_details_resource import AssetDetailsResource

# TODO update the JSON string below
json = "{}"
# create an instance of AssetDetailsResource from a JSON string
asset_details_resource_instance = AssetDetailsResource.from_json(json)
# print the JSON string representation of the object
print AssetDetailsResource.to_json()

# convert the object into a dict
asset_details_resource_dict = asset_details_resource_instance.to_dict()
# create an instance of AssetDetailsResource from a dict
asset_details_resource_form_dict = asset_details_resource.from_dict(asset_details_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


