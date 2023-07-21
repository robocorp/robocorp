<!-- markdownlint-disable -->

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.workitems`




**Variables**
---------------
- **inputs**
- **outputs**


---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/__init__.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `Inputs`
Inputs represents the input queue of work items. 

It can be used to reserve and release items from the queue, and iterate over them. 


---

#### <kbd>property</kbd> current

The current reserved input item. 

---

#### <kbd>property</kbd> released

A list of inputs reserved and released during the lifetime of the library. 



---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/__init__.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `reserve`

```python
reserve() → Input
```

Reserve a new input work item. 

There can only be one item reserved at a time. 



**Returns:**
 Input work item 



**Raises:**

 - <b>`RuntimeError`</b>:  An input work item is already reserved 
 - <b>`workitems.EmptyQueue`</b>:  There are no further items in the queue 


---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/__init__.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `Outputs`
Outputs represents the output queue of work items. 

It can be used to create outputs and inspect the items created during the execution. 


---

#### <kbd>property</kbd> last

The most recently created output work item, or `None`. 



---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/__init__.py#L137"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `create`

```python
create(
    payload: Optional[dict[str, Any], list[Any], str, int, float, bool] = None,
    files: Optional[str, list[str]] = None,
    save: bool = True
) → Output
```

Create a new output work item, which can have both a JSON payload and attached files. 

Creating an output item requires an input to be currently reserved. 



**Args:**

 - <b>`payload`</b>:  JSON serializable data (dict, list, scalar, etc.) 
 - <b>`files`</b>:  List of paths to files or glob pattern 
 - <b>`save`</b>:  Immediately save item after creation 



**Raises:**

 - <b>`RuntimeError`</b>:  No input work item reserved 


---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `Input`




<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `__init__`

```python
__init__(item_id: str, adapter: BaseAdapter)
```






---

#### <kbd>property</kbd> files





---

#### <kbd>property</kbd> id





---

#### <kbd>property</kbd> outputs





---

#### <kbd>property</kbd> payload





---

#### <kbd>property</kbd> released





---

#### <kbd>property</kbd> state







---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L183"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `create_output`

```python
create_output() → Output
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L188"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `done`

```python
done()
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L144"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `download_file`

```python
download_file(name: str, path: Optional[Path, str] = None) → Path
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L160"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `download_files`

```python
download_files(pattern: str, path: Optional[Path] = None) → List[Path]
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `email`

```python
email(html=True, encoding='utf-8', ignore_errors=False) → Optional[Email]
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L196"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `fail`

```python
fail(
    exception_type: Union[ExceptionType, str] = <ExceptionType.APPLICATION: 'APPLICATION'>,
    code: Optional[str] = None,
    message: Optional[str] = None
)
```






---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L222"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `Output`




<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L223"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `__init__`

```python
__init__(parent_id: str, adapter: BaseAdapter)
```






---

#### <kbd>property</kbd> files





---

#### <kbd>property</kbd> id





---

#### <kbd>property</kbd> parent_id





---

#### <kbd>property</kbd> payload





---

#### <kbd>property</kbd> saved







---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L286"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `add_file`

```python
add_file(path: Union[Path, str], name: Optional[str] = None) → Path
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L299"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `add_files`

```python
add_files(pattern: str) → list[Path]
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L271"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `save`

```python
save()
```






---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_types.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>enum</kbd> `State`
Work item state, after release. 


---
### <kbd>values</kbd>
- **DONE** = COMPLETED
- **FAILED** = FAILED



---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_types.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>enum</kbd> `ExceptionType`
Failed work item error type. 


---
### <kbd>values</kbd>
- **BUSINESS** = BUSINESS
- **APPLICATION** = APPLICATION



---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L6"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>exception</kbd> `EmptyQueue`
Raised when trying to load an input item and none available. 





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>exception</kbd> `BusinessException`
An exception that can be raised to release an input work item with a BUSINESS exception type. 

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `__init__`

```python
__init__(message: Optional[str] = None, code: Optional[str] = None)
```









---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L23"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>exception</kbd> `ApplicationException`
An exception that can be raised to release an input work item with a BUSINESS exception type. 

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `__init__`

```python
__init__(message: Optional[str] = None, code: Optional[str] = None)
```









---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `RobocorpAdapter`
Adapter for saving/loading work items from Robocorp Control Room. 

Required environment variables: 

* RC_API_WORKITEM_HOST:     Work item API hostname * RC_API_WORKITEM_TOKEN:    Work item API access token 

* RC_API_PROCESS_HOST:      Process API hostname * RC_API_PROCESS_TOKEN:     Process API access token 

* RC_WORKSPACE_ID:          Control room workspace ID * RC_PROCESS_ID:            Control room process ID * RC_PROCESS_RUN_ID:        Control room process run ID * RC_ROBOT_RUN_ID:          Control room robot run ID 

* RC_WORKITEM_ID:           Control room work item ID (input) 

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `__init__`

```python
__init__() → None
```








---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L249"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `add_file`

```python
add_file(item_id: str, name: str, original_name: str, content: bytes)
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L195"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `create_output`

```python
create_output(
    parent_id: str,
    payload: Optional[dict[str, Any], list[Any], str, int, float, bool] = None
) → str
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L284"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `file_id`

```python
file_id(item_id: str, name: str) → str
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L231"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `get_file`

```python
get_file(item_id: str, name: str) → bytes
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L223"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `list_files`

```python
list_files(item_id: str) → List[str]
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L204"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `load_payload`

```python
load_payload(
    item_id: str
) → Union[dict[str, Any], list[Any], str, int, float, bool, NoneType]
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L162"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `release_input`

```python
release_input(item_id: str, state: State, exception: Optional[dict] = None)
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L279"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `remove_file`

```python
remove_file(item_id: str, name: str)
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L151"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `reserve_input`

```python
reserve_input() → str
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L217"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `save_payload`

```python
save_payload(
    item_id: str,
    payload: Optional[dict[str, Any], list[Any], str, int, float, bool]
)
```






---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L302"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `FileAdapter`
Adapter for simulating work item input queues. 

Reads inputs from the given database file, and writes all created output items into an adjacent file with the suffix ``<filename>.output.json``. If the output path is provided by an env var explicitly, then the file will be saved with the provided path and name. 

Reads and writes all work item files from/to the same parent folder as the given input database. 

Optional environment variables: 

* RPA_INPUT_WORKITEM_PATH:  Path to work items input database file * RPA_OUTPUT_WORKITEM_PATH:  Path to work items output database file 

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L319"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `__init__`

```python
__init__() → None
```






---

#### <kbd>property</kbd> input_path





---

#### <kbd>property</kbd> output_path







---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L442"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `add_file`

```python
add_file(item_id: str, name: str, original_name: str, content: bytes)
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L405"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `create_output`

```python
create_output(
    _: str,
    payload: Optional[dict[str, Any], list[Any], str, int, float, bool] = None
) → str
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L428"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `get_file`

```python
get_file(item_id: str, name: str) → bytes
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L423"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `list_files`

```python
list_files(item_id: str) → List[str]
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L468"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `load_database`

```python
load_database() → List
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L414"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `load_payload`

```python
load_payload(
    item_id: str
) → Union[dict[str, Any], list[Any], str, int, float, bool, NoneType]
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L393"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `release_input`

```python
release_input(item_id: str, state: State, exception: Optional[dict] = None)
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L457"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `remove_file`

```python
remove_file(item_id: str, name: str)
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L384"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `reserve_input`

```python
reserve_input() → str
```





---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L418"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `save_payload`

```python
save_payload(
    item_id: str,
    payload: Optional[dict[str, Any], list[Any], str, int, float, bool]
)
```






---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `BaseAdapter`
Abstract base class for work item adapters. 




---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L58"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `add_file`

```python
add_file(item_id: str, name: str, original_name: str, content: bytes)
```

Attach file to work item. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L33"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `create_output`

```python
create_output(
    parent_id: str,
    payload: Optional[dict[str, Any], list[Any], str, int, float, bool] = None
) → str
```

Create new output for work item, and return created ID. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `get_file`

```python
get_file(item_id: str, name: str) → bytes
```

Read file's contents from work item. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L48"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `list_files`

```python
list_files(item_id: str) → List[str]
```

List attached files in work item. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `load_payload`

```python
load_payload(
    item_id: str
) → Union[dict[str, Any], list[Any], str, int, float, bool, NoneType]
```

Load JSON payload from work item. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L26"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `release_input`

```python
release_input(item_id: str, state: State, exception: Optional[dict] = None)
```

Release the lastly retrieved input work item and set state. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `remove_file`

```python
remove_file(item_id: str, name: str)
```

Remove attached file from work item. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L21"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `reserve_input`

```python
reserve_input() → str
```

Get next work item ID from the input queue and reserve it. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_adapters.py#L43"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `save_payload`

```python
save_payload(
    item_id: str,
    payload: Optional[dict[str, Any], list[Any], str, int, float, bool]
)
```

Save JSON payload to work item. 


