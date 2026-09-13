# GenericErrorResponse


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**error** | [**GenericErrorResponseError**](GenericErrorResponseError.md) |  | 

## Example

```python
from openapi_client.models.generic_error_response import GenericErrorResponse

# TODO update the JSON string below
json = "{}"
# create an instance of GenericErrorResponse from a JSON string
generic_error_response_instance = GenericErrorResponse.from_json(json)
# print the JSON string representation of the object
print GenericErrorResponse.to_json()

# convert the object into a dict
generic_error_response_dict = generic_error_response_instance.to_dict()
# create an instance of GenericErrorResponse from a dict
generic_error_response_form_dict = generic_error_response.from_dict(generic_error_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


