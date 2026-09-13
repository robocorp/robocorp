# CreateAssetUpload200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**status** | **str** |  | 
**content_type** | **str** |  | 
**upload_url** | **str** |  | 

## Example

```python
from openapi_client.models.create_asset_upload200_response import CreateAssetUpload200Response

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAssetUpload200Response from a JSON string
create_asset_upload200_response_instance = CreateAssetUpload200Response.from_json(json)
# print the JSON string representation of the object
print CreateAssetUpload200Response.to_json()

# convert the object into a dict
create_asset_upload200_response_dict = create_asset_upload200_response_instance.to_dict()
# create an instance of CreateAssetUpload200Response from a dict
create_asset_upload200_response_form_dict = create_asset_upload200_response.from_dict(create_asset_upload200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


