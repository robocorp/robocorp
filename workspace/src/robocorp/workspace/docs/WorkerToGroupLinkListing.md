# WorkerToGroupLinkListing


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**worker** | [**AddWorkerToGroupRequestWorker**](AddWorkerToGroupRequestWorker.md) |  | 
**worker_groups** | [**List[ListAssets200ResponseDataInner]**](ListAssets200ResponseDataInner.md) |  | 

## Example

```python
from workspace.models.worker_to_group_link_listing import WorkerToGroupLinkListing

# TODO update the JSON string below
json = "{}"
# create an instance of WorkerToGroupLinkListing from a JSON string
worker_to_group_link_listing_instance = WorkerToGroupLinkListing.from_json(json)
# print the JSON string representation of the object
print WorkerToGroupLinkListing.to_json()

# convert the object into a dict
worker_to_group_link_listing_dict = worker_to_group_link_listing_instance.to_dict()
# create an instance of WorkerToGroupLinkListing from a dict
worker_to_group_link_listing_form_dict = worker_to_group_link_listing.from_dict(worker_to_group_link_listing_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


