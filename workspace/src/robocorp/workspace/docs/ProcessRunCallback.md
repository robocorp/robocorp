# ProcessRunCallback


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**url** | **str** |  | 
**secret** | **str** |  | 
**callback_events** | **List[str]** |  | 

## Example

```python
from robocorp.workspace.models.process_run_callback import ProcessRunCallback

# TODO update the JSON string below
json = "{}"
# create an instance of ProcessRunCallback from a JSON string
process_run_callback_instance = ProcessRunCallback.from_json(json)
# print the JSON string representation of the object
print ProcessRunCallback.to_json()

# convert the object into a dict
process_run_callback_dict = process_run_callback_instance.to_dict()
# create an instance of ProcessRunCallback from a dict
process_run_callback_form_dict = process_run_callback.from_dict(process_run_callback_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


