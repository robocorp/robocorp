# ListAssistants200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next** | [**Next**](Next.md) |  | 
**has_more** | [**HasMore**](HasMore.md) |  | 
**data** | [**List[AssistantResource]**](AssistantResource.md) |  | 

## Example

```python
from workspace.models.list_assistants200_response import ListAssistants200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListAssistants200Response from a JSON string
list_assistants200_response_instance = ListAssistants200Response.from_json(json)
# print the JSON string representation of the object
print ListAssistants200Response.to_json()

# convert the object into a dict
list_assistants200_response_dict = list_assistants200_response_instance.to_dict()
# create an instance of ListAssistants200Response from a dict
list_assistants200_response_form_dict = list_assistants200_response.from_dict(list_assistants200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


