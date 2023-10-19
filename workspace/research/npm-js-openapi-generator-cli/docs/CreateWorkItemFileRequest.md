# CreateWorkItemFileRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**file_name** | **str** |  | 
**file_size** | **float** |  | 

## Example

```python
from openapi_client.models.create_work_item_file_request import CreateWorkItemFileRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateWorkItemFileRequest from a JSON string
create_work_item_file_request_instance = CreateWorkItemFileRequest.from_json(json)
# print the JSON string representation of the object
print CreateWorkItemFileRequest.to_json()

# convert the object into a dict
create_work_item_file_request_dict = create_work_item_file_request_instance.to_dict()
# create an instance of CreateWorkItemFileRequest from a dict
create_work_item_file_request_form_dict = create_work_item_file_request.from_dict(create_work_item_file_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


