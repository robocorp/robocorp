# ProcessRunResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**state** | **str** |  | 
**created_at** | **datetime** |  | 
**started_at** | **datetime** |  | 
**ended_at** | **datetime** |  | 
**process** | [**ListAssets200ResponseDataInner**](ListAssets200ResponseDataInner.md) |  | 
**started_by** | [**ProcessRunResourceStartedBy**](ProcessRunResourceStartedBy.md) |  | 
**duration** | **float** | Process run duration in seconds | 

## Example

```python
from openapi_client.models.process_run_resource import ProcessRunResource

# TODO update the JSON string below
json = "{}"
# create an instance of ProcessRunResource from a JSON string
process_run_resource_instance = ProcessRunResource.from_json(json)
# print the JSON string representation of the object
print ProcessRunResource.to_json()

# convert the object into a dict
process_run_resource_dict = process_run_resource_instance.to_dict()
# create an instance of ProcessRunResource from a dict
process_run_resource_form_dict = process_run_resource.from_dict(process_run_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


