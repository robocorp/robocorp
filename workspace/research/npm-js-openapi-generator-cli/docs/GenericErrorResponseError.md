# GenericErrorResponseError


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** |  | 
**message** | **str** |  | 

## Example

```python
from openapi_client.models.generic_error_response_error import GenericErrorResponseError

# TODO update the JSON string below
json = "{}"
# create an instance of GenericErrorResponseError from a JSON string
generic_error_response_error_instance = GenericErrorResponseError.from_json(json)
# print the JSON string representation of the object
print GenericErrorResponseError.to_json()

# convert the object into a dict
generic_error_response_error_dict = generic_error_response_error_instance.to_dict()
# create an instance of GenericErrorResponseError from a dict
generic_error_response_error_form_dict = generic_error_response_error.from_dict(generic_error_response_error_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


