# ListAssets200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[ListAssets200ResponseDataInner]**](ListAssets200ResponseDataInner.md) |  | 
**has_more** | **bool** | Whether or not there are more elements available after this set. If false, this set comprises the end of the list. | 
**next** | **str** | The full URL to access the next set of results. Null if there are no next set of results. | 

## Example

```python
from robocorp.workspace.models.list_assets200_response import ListAssets200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListAssets200Response from a JSON string
list_assets200_response_instance = ListAssets200Response.from_json(json)
# print the JSON string representation of the object
print ListAssets200Response.to_json()

# convert the object into a dict
list_assets200_response_dict = list_assets200_response_instance.to_dict()
# create an instance of ListAssets200Response from a dict
list_assets200_response_form_dict = list_assets200_response.from_dict(list_assets200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


