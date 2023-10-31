# ListStepRunConsoleMessages200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next** | [**Next**](Next.md) |  | 
**has_more** | [**HasMore**](HasMore.md) |  | 
**data** | [**List[ListStepRunConsoleMessages200ResponseDataInner]**](ListStepRunConsoleMessages200ResponseDataInner.md) |  | 

## Example

```python
from robocorp.workspace.models.list_step_run_console_messages200_response import ListStepRunConsoleMessages200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListStepRunConsoleMessages200Response from a JSON string
list_step_run_console_messages200_response_instance = ListStepRunConsoleMessages200Response.from_json(json)
# print the JSON string representation of the object
print ListStepRunConsoleMessages200Response.to_json()

# convert the object into a dict
list_step_run_console_messages200_response_dict = list_step_run_console_messages200_response_instance.to_dict()
# create an instance of ListStepRunConsoleMessages200Response from a dict
list_step_run_console_messages200_response_form_dict = list_step_run_console_messages200_response.from_dict(list_step_run_console_messages200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


