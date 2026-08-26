# CreateWorkerGroupLinkTokenRequest


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | 
**expires_at** | **datetime** |  | 

## Example

```python
from openapi_client.models.create_worker_group_link_token_request import CreateWorkerGroupLinkTokenRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CreateWorkerGroupLinkTokenRequest from a JSON string
create_worker_group_link_token_request_instance = CreateWorkerGroupLinkTokenRequest.from_json(json)
# print the JSON string representation of the object
print CreateWorkerGroupLinkTokenRequest.to_json()

# convert the object into a dict
create_worker_group_link_token_request_dict = create_worker_group_link_token_request_instance.to_dict()
# create an instance of CreateWorkerGroupLinkTokenRequest from a dict
create_worker_group_link_token_request_form_dict = create_worker_group_link_token_request.from_dict(create_worker_group_link_token_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


