# WorkspaceResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**name** | **str** |  | 
**organization** | [**ListAssets200ResponseDataInner**](ListAssets200ResponseDataInner.md) |  | 

## Example

```python
from openapi_client.models.workspace_resource import WorkspaceResource

# TODO update the JSON string below
json = "{}"
# create an instance of WorkspaceResource from a JSON string
workspace_resource_instance = WorkspaceResource.from_json(json)
# print the JSON string representation of the object
print WorkspaceResource.to_json()

# convert the object into a dict
workspace_resource_dict = workspace_resource_instance.to_dict()
# create an instance of WorkspaceResource from a dict
workspace_resource_form_dict = workspace_resource.from_dict(workspace_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


