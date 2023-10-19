# EmptyAssetDetailsResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**payload** | [**EmptyAssetDetailsResourcePayload**](EmptyAssetDetailsResourcePayload.md) |  | 

## Example

```python
from workspace.models.empty_asset_details_resource import EmptyAssetDetailsResource

# TODO update the JSON string below
json = "{}"
# create an instance of EmptyAssetDetailsResource from a JSON string
empty_asset_details_resource_instance = EmptyAssetDetailsResource.from_json(json)
# print the JSON string representation of the object
print EmptyAssetDetailsResource.to_json()

# convert the object into a dict
empty_asset_details_resource_dict = empty_asset_details_resource_instance.to_dict()
# create an instance of EmptyAssetDetailsResource from a dict
empty_asset_details_resource_form_dict = empty_asset_details_resource.from_dict(empty_asset_details_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


