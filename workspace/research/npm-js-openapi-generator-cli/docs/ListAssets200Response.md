# ListAssets200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**data** | [**List[ListAssets200ResponseDataInner]**](ListAssets200ResponseDataInner.md) |  | 

## Example

```python
from openapi_client.models.list_assets200_response import ListAssets200Response

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


