# LinkTokenResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**expires_at** | **datetime** |  | 
**link_token** | **str** |  | 

## Example

```python
from workspace.models.link_token_resource import LinkTokenResource

# TODO update the JSON string below
json = "{}"
# create an instance of LinkTokenResource from a JSON string
link_token_resource_instance = LinkTokenResource.from_json(json)
# print the JSON string representation of the object
print LinkTokenResource.to_json()

# convert the object into a dict
link_token_resource_dict = link_token_resource_instance.to_dict()
# create an instance of LinkTokenResource from a dict
link_token_resource_form_dict = link_token_resource.from_dict(link_token_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


