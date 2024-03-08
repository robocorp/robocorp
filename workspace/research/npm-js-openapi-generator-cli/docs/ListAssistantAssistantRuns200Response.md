# ListAssistantAssistantRuns200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next** | [**Next**](Next.md) |  | 
**has_more** | [**HasMore**](HasMore.md) |  | 
**data** | [**List[AssistantRunResource]**](AssistantRunResource.md) |  | 

## Example

```python
from openapi_client.models.list_assistant_assistant_runs200_response import ListAssistantAssistantRuns200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListAssistantAssistantRuns200Response from a JSON string
list_assistant_assistant_runs200_response_instance = ListAssistantAssistantRuns200Response.from_json(json)
# print the JSON string representation of the object
print ListAssistantAssistantRuns200Response.to_json()

# convert the object into a dict
list_assistant_assistant_runs200_response_dict = list_assistant_assistant_runs200_response_instance.to_dict()
# create an instance of ListAssistantAssistantRuns200Response from a dict
list_assistant_assistant_runs200_response_form_dict = list_assistant_assistant_runs200_response.from_dict(list_assistant_assistant_runs200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


