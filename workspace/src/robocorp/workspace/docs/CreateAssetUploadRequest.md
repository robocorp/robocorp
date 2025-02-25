# CreateAssetUploadRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**content_type** | **str** |  | 
**data** | **str** |  | [optional] 

## Example

```python
from robocorp.workspace.models.create_asset_upload_request import CreateAssetUploadRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateAssetUploadRequest from a JSON string
create_asset_upload_request_instance = CreateAssetUploadRequest.from_json(json)
# print the JSON string representation of the object
print CreateAssetUploadRequest.to_json()

# convert the object into a dict
create_asset_upload_request_dict = create_asset_upload_request_instance.to_dict()
# create an instance of CreateAssetUploadRequest from a dict
create_asset_upload_request_form_dict = create_asset_upload_request.from_dict(create_asset_upload_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


