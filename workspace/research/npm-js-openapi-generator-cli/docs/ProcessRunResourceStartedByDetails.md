# ProcessRunResourceStartedByDetails

Details are only available when the process run was started by a `user`

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**first_name** | **str** |  | 
**last_name** | **str** |  | 

## Example

```python
from openapi_client.models.process_run_resource_started_by_details import ProcessRunResourceStartedByDetails

# TODO update the JSON string below
json = "{}"
# create an instance of ProcessRunResourceStartedByDetails from a JSON string
process_run_resource_started_by_details_instance = ProcessRunResourceStartedByDetails.from_json(json)
# print the JSON string representation of the object
print ProcessRunResourceStartedByDetails.to_json()

# convert the object into a dict
process_run_resource_started_by_details_dict = process_run_resource_started_by_details_instance.to_dict()
# create an instance of ProcessRunResourceStartedByDetails from a dict
process_run_resource_started_by_details_form_dict = process_run_resource_started_by_details.from_dict(process_run_resource_started_by_details_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


