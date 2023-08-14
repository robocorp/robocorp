<!-- markdownlint-disable -->

# module `robocorp.workitems` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/__init__.py#L0)




## Variables
- **inputs**
- **outputs**



---

## class `Inputs` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/__init__.py#L65)

Inputs represents the input queue of work items.

It can be used to reserve and release items from the queue, and iterate over them.


---

#### property current

The current reserved input item.

---

#### property released

A list of inputs reserved and released during the lifetime of the library.



---

### method `reserve` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/__init__.py#L96)


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

## class `Outputs` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/__init__.py#L111)

Outputs represents the output queue of work items.

It can be used to create outputs and inspect the items created during the execution.


---

#### property last

The most recently created output work item, or `None`.



---

### method `create` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/__init__.py#L137)


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

## class `Input` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L206)

Container for an input work item.

An input work item can contain arbitrary JSON data in the `payload` section, and optionally attached files that are stored in Control Room.

Each step run of a process in Control Room has at least one input work item associated with it, but the step's input queue can have multiple input items in it.

There can only be one input work item reserved at a time. To reserve the next item, the current item needs to be released as either passed or failed.

### method `__init__` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L221)


```python
__init__(adapter: BaseAdapter, item_id: str)
```





---

#### property files

Names of attached files.

---

#### property id

Current ID for work item.

---

#### property outputs

Child output work items.

---

#### property parent_id

Current parent work item ID (output only).

---

#### property payload

Current JSON payload.

---

#### property released

Is the current item released.

---

#### property saved

Is the current item saved.

---

#### property state

Current release state.



---

### method `add_file` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L117)


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

### method `add_files` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L144)


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

### method `create_output` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L430)


```python
create_output() → Output
```

Create an output work item that is a child of this item.

---

### method `done` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L438)


```python
done()
```

Mark this work item as done, and release it.

---

### method `email` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L284)


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

### method `fail` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L449)


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

### method `get_file` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L362)


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

### method `get_files` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L392)


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

### method `load` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L72)


```python
load() → None
```

Load work item payload and file listing from Control Room.

---

### method `remove_file` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L166)


```python
remove_file(name: str, missing_ok: bool = False)
```

Remove attached file with given name.

Note: Files are not removed from Control Room until the item is saved.



**Args:**

 - <b>`name`</b>:  Name of file
 - <b>`missing_ok`</b>:  Do nothing if given file does not exist

---

### method `remove_files` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L185)


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

### method `save` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L273)


```python
save()
```

Save the current input work item.

Updates the work item payload and adds/removes all pending files.

**Note:** Modifying input work items is not recommended, as it will make traceability after execution difficult, and potentially makethe process behave in unexpected ways.


---

## class `Output` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L507)

Container for an output work item.

Created output items are added to an output queue, and released to the next step of a process when the current run ends.

Note: An output item always has an input item as a parent, which is used for traceability in a work item's history.

### method `__init__` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L517)


```python
__init__(adapter: BaseAdapter, parent_id: str)
```





---

#### property files

Names of attached files.

---

#### property id

Current ID for work item.

---

#### property parent_id

Current parent work item ID (output only).

---

#### property payload

Current JSON payload.

---

#### property saved

Is the current item saved.



---

### method `add_file` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L117)


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

### method `add_files` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L144)


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

### method `load` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L72)


```python
load() → None
```

Load work item payload and file listing from Control Room.

---

### method `remove_file` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L166)


```python
remove_file(name: str, missing_ok: bool = False)
```

Remove attached file with given name.

Note: Files are not removed from Control Room until the item is saved.



**Args:**

 - <b>`name`</b>:  Name of file
 - <b>`missing_ok`</b>:  Do nothing if given file does not exist

---

### method `remove_files` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L185)


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

### method `save` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_workitem.py#L81)


```python
save()
```

Save the current work item.

Updates the work item payload and adds/removes all pending files.


---

## enum `State` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_types.py#L15)

Work item state, after release.


---
### values
- **DONE** = COMPLETED
- **FAILED** = FAILED



---

## enum `ExceptionType` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_types.py#L22)

Failed work item error type.


---
### values
- **BUSINESS** = BUSINESS
- **APPLICATION** = APPLICATION



---

## exception `EmptyQueue` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L6)

Raised when trying to load an input item and none available.





---

## exception `BusinessException` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L16)

An exception that can be raised to release an input work item with a BUSINESS exception type.

### method `__init__` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L11)


```python
__init__(message: Optional[str] = None, code: Optional[str] = None)
```








---

## exception `ApplicationException` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L23)

An exception that can be raised to release an input work item with a BUSINESS exception type.

### method `__init__` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L11)


```python
__init__(message: Optional[str] = None, code: Optional[str] = None)
```








