# PaginationDetails


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**next** | **str** | The full URL to access the next set of results. Null if there are no next set of results. | 
**has_more** | **bool** | Whether or not there are more elements available after this set. If false, this set comprises the end of the list. | 

## Example

```python
from workspace.models.pagination_details import PaginationDetails

# TODO update the JSON string below
json = "{}"
# create an instance of PaginationDetails from a JSON string
pagination_details_instance = PaginationDetails.from_json(json)
# print the JSON string representation of the object
print PaginationDetails.to_json()

# convert the object into a dict
pagination_details_dict = pagination_details_instance.to_dict()
# create an instance of PaginationDetails from a dict
pagination_details_form_dict = pagination_details.from_dict(pagination_details_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


