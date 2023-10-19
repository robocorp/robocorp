# WorkItemException


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**code** | **str** |  | 
**type** | **str** |  | 
**message** | **str** |  | 

## Example

```python
from openapi_client.models.work_item_exception import WorkItemException

# TODO update the JSON string below
json = "{}"
# create an instance of WorkItemException from a JSON string
work_item_exception_instance = WorkItemException.from_json(json)
# print the JSON string representation of the object
print WorkItemException.to_json()

# convert the object into a dict
work_item_exception_dict = work_item_exception_instance.to_dict()
# create an instance of WorkItemException from a dict
work_item_exception_form_dict = work_item_exception.from_dict(work_item_exception_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


