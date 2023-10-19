# CreateWorkItemFile200Response


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** |  | 
**form_data** | **object** | The form data fields you must include when uploading the file | 

## Example

```python
from openapi_client.models.create_work_item_file200_response import CreateWorkItemFile200Response

# TODO update the JSON string below
json = "{}"
# create an instance of CreateWorkItemFile200Response from a JSON string
create_work_item_file200_response_instance = CreateWorkItemFile200Response.from_json(json)
# print the JSON string representation of the object
print CreateWorkItemFile200Response.to_json()

# convert the object into a dict
create_work_item_file200_response_dict = create_work_item_file200_response_instance.to_dict()
# create an instance of CreateWorkItemFile200Response from a dict
create_work_item_file200_response_form_dict = create_work_item_file200_response.from_dict(create_work_item_file200_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


