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

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L206"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `Input`
Container for an input work item. 

An input work item can contain arbitrary JSON data in the `payload` section, and optionally attached files that are stored in Control Room. 

Each step run of a process in Control Room has at least one input work item associated with it, but the step's input queue can have multiple input items in it. 

There can only be one input work item reserved at a time. To reserve the next item, the current item needs to be released as either passed or failed. 

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L221"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `__init__`

```python
__init__(adapter: BaseAdapter, item_id: str)
```






---

#### <kbd>property</kbd> files

Names of attached files. 

---

#### <kbd>property</kbd> id

Current ID for work item. 

---

#### <kbd>property</kbd> outputs

Child output work items. 

---

#### <kbd>property</kbd> parent_id

Current parent work item ID (output only). 

---

#### <kbd>property</kbd> payload

Current JSON payload. 

---

#### <kbd>property</kbd> released

Is the current item released. 

---

#### <kbd>property</kbd> saved

Is the current item saved. 

---

#### <kbd>property</kbd> state

Current release state. 



---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `add_file`

```python
add_file(path: Union[Path, str], name: Optional[str] = None) → Path
```

Attach a file from the local machine to the work item. 

Note: Files are not uploaded until the item is saved. 



**Args:**

 - <b>`path`</b>:  Path to attached file 
 - <b>`name`</b>:  Custom name for file in work item 



**Returns:**
Resolved path to added file 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L144"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `add_files`

```python
add_files(pattern: str) → list[Path]
```

Attach files from the local machine to the work item that match the given pattern. 

Note: Files are not uploaded until the item is saved. 



**Args:**

 - <b>`pattern`</b>:  Glob pattern for attached file paths 



**Returns:**
List of added paths 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L430"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `create_output`

```python
create_output() → Output
```

Create an output work item that is a child of this item. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L438"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `done`

```python
done()
```

Mark this work item as done, and release it. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L284"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `email`

```python
email(html=True, encoding='utf-8', ignore_errors=False) → Optional[Email]
```

Parse an email attachment from the work item. 



**Args:**

 - <b>`html`</b>:  Parse the HTML content into the `html` attribute 
 - <b>`encoding`</b>:  Text encoding of the email 
 - <b>`ignore_errors`</b>:  Ignore possible parsing errors from Control Room 



**Returns:**
An email container with metadata and content 



**Raises:**

 - <b>`ValueError`</b>:  No email attached or content is malformed 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L449"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `fail`

```python
fail(
    exception_type: Union[ExceptionType, str] = <ExceptionType.APPLICATION: 'APPLICATION'>,
    code: Optional[str] = None,
    message: Optional[str] = None
)
```

Mark this work item as failed, and release it. 



**Args:**

 - <b>`exception_type`</b>:  Type of failure (APPLICATION or BUSINESS) 
 - <b>`code`</b>:  Custom error code for the failure 
 - <b>`message`</b>:  Human-readable error message 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L362"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `get_file`

```python
get_file(name: str, path: Optional[Path, str] = None) → Path
```

Download file with given name. 

If a `path` is not defined, uses the Robot root or current working directory. 



**Args:**

 - <b>`name`</b>:  Name of file 
 - <b>`path`</b>:  Path to created file 



**Returns:**
Path to created file 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L392"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `get_files`

```python
get_files(pattern: str, path: Optional[Path] = None) → list[Path]
```

Download all files attached to this work item that match the given pattern. 

If a `path` is not defined, uses the Robot root or current working directory. 



**Args:**

 - <b>`pattern`</b>:  Glob pattern for file names 
 - <b>`path`</b>:  Directory to store files in 



**Returns:**
List of created file paths 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `load`

```python
load() → None
```

Load work item payload and file listing from Control Room. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L166"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `remove_file`

```python
remove_file(name: str, missing_ok: bool = False)
```

Remove attached file with given name. 

Note: Files are not removed from Control Room until the item is saved. 



**Args:**

 - <b>`name`</b>:  Name of file 
 - <b>`missing_ok`</b>:  Do nothing if given file does not exist 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `remove_files`

```python
remove_files(pattern: str) → list[str]
```

Remove attached files that match the given pattern. 

Note: Files are not removed from Control Room until the item is saved. 



**Args:**

 - <b>`pattern`</b>:  Glob pattern for file names 



**Returns:**
List of matched names 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L273"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `save`

```python
save()
```

Save the current input work item. 

Updates the work item payload and adds/removes all pending files. 

**Note:** Modifying input work items is not recommended, as it will make traceability after execution difficult, and potentially make the process behave in unexpected ways. 


---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L507"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `Output`
Container for an output work item. 

Created output items are added to an output queue, and released to the next step of a process when the current run ends. 

Note: An output item always has an input item as a parent, which is used for traceability in a work item's history. 

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L517"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `__init__`

```python
__init__(adapter: BaseAdapter, parent_id: str)
```






---

#### <kbd>property</kbd> files

Names of attached files. 

---

#### <kbd>property</kbd> id

Current ID for work item. 

---

#### <kbd>property</kbd> parent_id

Current parent work item ID (output only). 

---

#### <kbd>property</kbd> payload

Current JSON payload. 

---

#### <kbd>property</kbd> saved

Is the current item saved. 



---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `add_file`

```python
add_file(path: Union[Path, str], name: Optional[str] = None) → Path
```

Attach a file from the local machine to the work item. 

Note: Files are not uploaded until the item is saved. 



**Args:**

 - <b>`path`</b>:  Path to attached file 
 - <b>`name`</b>:  Custom name for file in work item 



**Returns:**
Resolved path to added file 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L144"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `add_files`

```python
add_files(pattern: str) → list[Path]
```

Attach files from the local machine to the work item that match the given pattern. 

Note: Files are not uploaded until the item is saved. 



**Args:**

 - <b>`pattern`</b>:  Glob pattern for attached file paths 



**Returns:**
List of added paths 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `load`

```python
load() → None
```

Load work item payload and file listing from Control Room. 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L166"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `remove_file`

```python
remove_file(name: str, missing_ok: bool = False)
```

Remove attached file with given name. 

Note: Files are not removed from Control Room until the item is saved. 



**Args:**

 - <b>`name`</b>:  Name of file 
 - <b>`missing_ok`</b>:  Do nothing if given file does not exist 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L185"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `remove_files`

```python
remove_files(pattern: str) → list[str]
```

Remove attached files that match the given pattern. 

Note: Files are not removed from Control Room until the item is saved. 



**Args:**

 - <b>`pattern`</b>:  Glob pattern for file names 



**Returns:**
List of matched names 

---

<a href="https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `save`

```python
save()
```

Save the current work item. 

Updates the work item payload and adds/removes all pending files. 


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









