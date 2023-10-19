# ProcessRunOutputResource


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**id** | **str** |  | 
**created_at** | **datetime** |  | 
**process** | [**ProcessReferenceResource**](.md) |  | 
**process_run** | [**ProcessRunReferenceResource**](.md) |  | 
**payload** | [**AnyValidJson**](AnyValidJson.md) |  | 
**files** | [**List[WorkItemFile]**](WorkItemFile.md) |  | 

## Example

```python
from workspace.models.process_run_output_resource import ProcessRunOutputResource

# TODO update the JSON string below
json = "{}"
# create an instance of ProcessRunOutputResource from a JSON string
process_run_output_resource_instance = ProcessRunOutputResource.from_json(json)
# print the JSON string representation of the object
print ProcessRunOutputResource.to_json()

# convert the object into a dict
process_run_output_resource_dict = process_run_output_resource_instance.to_dict()
# create an instance of ProcessRunOutputResource from a dict
process_run_output_resource_form_dict = process_run_output_resource.from_dict(process_run_output_resource_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


