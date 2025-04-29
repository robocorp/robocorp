# ListProcessRunWorkItems200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next** | [**Next**](Next.md) |  | 
**has_more** | [**HasMore**](HasMore.md) |  | 
**data** | [**List[ListProcessRunWorkItems200ResponseDataInner]**](ListProcessRunWorkItems200ResponseDataInner.md) |  | 

## Example

```python
from openapi_client.models.list_process_run_work_items200_response import ListProcessRunWorkItems200Response

# TODO update the JSON string below
json = "{}"
# create an instance of ListProcessRunWorkItems200Response from a JSON string
list_process_run_work_items200_response_instance = ListProcessRunWorkItems200Response.from_json(json)
# print the JSON string representation of the object
print ListProcessRunWorkItems200Response.to_json()

# convert the object into a dict
list_process_run_work_items200_response_dict = list_process_run_work_items200_response_instance.to_dict()
# create an instance of ListProcessRunWorkItems200Response from a dict
list_process_run_work_items200_response_form_dict = list_process_run_work_items200_response.from_dict(list_process_run_work_items200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


