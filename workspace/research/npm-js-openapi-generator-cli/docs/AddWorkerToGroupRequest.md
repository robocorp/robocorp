# AddWorkerToGroupRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**worker** | [**AddWorkerToGroupRequestWorker**](AddWorkerToGroupRequestWorker.md) |  | 

## Example

```python
from openapi_client.models.add_worker_to_group_request import AddWorkerToGroupRequest

# TODO update the JSON string below
json = "{}"
# create an instance of AddWorkerToGroupRequest from a JSON string
add_worker_to_group_request_instance = AddWorkerToGroupRequest.from_json(json)
# print the JSON string representation of the object
print AddWorkerToGroupRequest.to_json()

# convert the object into a dict
add_worker_to_group_request_dict = add_worker_to_group_request_instance.to_dict()
# create an instance of AddWorkerToGroupRequest from a dict
add_worker_to_group_request_form_dict = add_worker_to_group_request.from_dict(add_worker_to_group_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


