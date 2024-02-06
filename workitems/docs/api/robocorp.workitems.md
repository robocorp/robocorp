<!-- markdownlint-disable -->

# module `robocorp.workitems`

**Source:** [`__init__.py:0`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/__init__.py#L0)

## Variables

- **inputs**
- **outputs**

______________________________________________________________________

## class `Inputs`

**Source:** [`__init__.py:65`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/__init__.py#L65)

Inputs represents the input queue of work items.

It can be used to reserve and release items from the queue, and iterate over them.

#### property `current`

The current reserved input item.

#### property `released`

A list of inputs reserved and released during the lifetime of the library.

______________________________________________________________________

### method `reserve`

**Source:** [`__init__.py:98`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/__init__.py#L98)

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

______________________________________________________________________

## class `Outputs`

**Source:** [`__init__.py:113`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/__init__.py#L113)

Outputs represents the output queue of work items.

It can be used to create outputs and inspect the items created during the execution.

#### property `last`

The most recently created output work item, or `None`.

______________________________________________________________________

### method `create`

**Source:** [`__init__.py:139`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/__init__.py#L139)

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

______________________________________________________________________

## class `Input`

**Source:** [`_workitem.py:207`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L207)

Container for an input work item.

An input work item can contain arbitrary JSON data in the `payload` section, and optionally attached files that are stored in Control Room.

Each step run of a process in Control Room has at least one input work item associated with it, but the step's input queue can have multiple input items in it.

There can only be one input work item reserved at a time. To reserve the next item, the current item needs to be released as either passed or failed.

### method `__init__`

**Source:** [`_workitem.py:222`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L222)

```python
__init__(adapter: BaseAdapter, item_id: str)
```

#### property `exception`

Current work item exception if any.

#### property `files`

Names of attached files.

#### property `id`

Current ID for work item.

#### property `outputs`

Child output work items.

#### property `parent_id`

Current parent work item ID (output only).

#### property `payload`

Current JSON payload.

#### property `released`

Is the current item released.

#### property `saved`

Is the current item saved.

#### property `state`

Current release state.

______________________________________________________________________

### method `add_file`

**Source:** [`_workitem.py:118`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L118)

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

______________________________________________________________________

### method `add_files`

**Source:** [`_workitem.py:145`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L145)

```python
add_files(pattern: str) → list[Path]
```

Attach files from the local machine to the work item that match the given pattern.

Note: Files are not uploaded until the item is saved.

**Args:**

- <b>`pattern`</b>:  Glob pattern for attached file paths

**Returns:**
List of added paths

______________________________________________________________________

### method `create_output`

**Source:** [`_workitem.py:440`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L440)

```python
create_output() → Output
```

Create an output work item that is a child of this item.

______________________________________________________________________

### method `done`

**Source:** [`_workitem.py:448`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L448)

```python
done()
```

Mark this work item as done, and release it.

______________________________________________________________________

### method `email`

**Source:** [`_workitem.py:294`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L294)

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

______________________________________________________________________

### method `fail`

**Source:** [`_workitem.py:459`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L459)

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

______________________________________________________________________

### method `get_file`

**Source:** [`_workitem.py:372`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L372)

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

______________________________________________________________________

### method `get_files`

**Source:** [`_workitem.py:402`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L402)

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

______________________________________________________________________

### method `load`

**Source:** [`_workitem.py:72`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L72)

```python
load() → None
```

Load work item payload and file listing from Control Room.

______________________________________________________________________

### method `remove_file`

**Source:** [`_workitem.py:167`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L167)

```python
remove_file(name: str, missing_ok: bool = False)
```

Remove attached file with given name.

Note: Files are not removed from Control Room until the item is saved.

**Args:**

- <b>`name`</b>:  Name of file
- <b>`missing_ok`</b>:  Do nothing if given file does not exist

______________________________________________________________________

### method `remove_files`

**Source:** [`_workitem.py:186`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L186)

```python
remove_files(pattern: str) → list[str]
```

Remove attached files that match the given pattern.

Note: Files are not removed from Control Room until the item is saved.

**Args:**

- <b>`pattern`</b>:  Glob pattern for file names

**Returns:**
List of matched names

______________________________________________________________________

### method `save`

**Source:** [`_workitem.py:283`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L283)

```python
save()
```

Save the current input work item.

Updates the work item payload and adds/removes all pending files.

**Note:** Modifying input work items is not recommended, as it will make traceability after execution difficult, and potentially makethe process behave in unexpected ways.

______________________________________________________________________

## class `Output`

**Source:** [`_workitem.py:518`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L518)

Container for an output work item.

Created output items are added to an output queue, and released to the next step of a process when the current run ends.

Note: An output item always has an input item as a parent, which is used for traceability in a work item's history.

### method `__init__`

**Source:** [`_workitem.py:528`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L528)

```python
__init__(adapter: BaseAdapter, parent_id: str)
```

#### property `files`

Names of attached files.

#### property `id`

Current ID for work item.

#### property `parent_id`

Current parent work item ID (output only).

#### property `payload`

Current JSON payload.

#### property `saved`

Is the current item saved.

______________________________________________________________________

### method `add_file`

**Source:** [`_workitem.py:118`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L118)

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

______________________________________________________________________

### method `add_files`

**Source:** [`_workitem.py:145`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L145)

```python
add_files(pattern: str) → list[Path]
```

Attach files from the local machine to the work item that match the given pattern.

Note: Files are not uploaded until the item is saved.

**Args:**

- <b>`pattern`</b>:  Glob pattern for attached file paths

**Returns:**
List of added paths

______________________________________________________________________

### method `load`

**Source:** [`_workitem.py:72`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L72)

```python
load() → None
```

Load work item payload and file listing from Control Room.

______________________________________________________________________

### method `remove_file`

**Source:** [`_workitem.py:167`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L167)

```python
remove_file(name: str, missing_ok: bool = False)
```

Remove attached file with given name.

Note: Files are not removed from Control Room until the item is saved.

**Args:**

- <b>`name`</b>:  Name of file
- <b>`missing_ok`</b>:  Do nothing if given file does not exist

______________________________________________________________________

### method `remove_files`

**Source:** [`_workitem.py:186`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L186)

```python
remove_files(pattern: str) → list[str]
```

Remove attached files that match the given pattern.

Note: Files are not removed from Control Room until the item is saved.

**Args:**

- <b>`pattern`</b>:  Glob pattern for file names

**Returns:**
List of matched names

______________________________________________________________________

### method `save`

**Source:** [`_workitem.py:82`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L82)

```python
save()
```

Save the current work item.

Updates the work item payload and adds/removes all pending files.

______________________________________________________________________

## enum `State`

**Source:** [`_types.py:15`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_types.py#L15)

Work item state, after release.

### Values

- **DONE** = COMPLETED
- **FAILED** = FAILED

______________________________________________________________________

## enum `ExceptionType`

**Source:** [`_types.py:22`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_types.py#L22)

Failed work item error type.

### Values

- **BUSINESS** = BUSINESS
- **APPLICATION** = APPLICATION

______________________________________________________________________

## exception `EmptyQueue`

**Source:** [`_exceptions.py:6`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L6)

Raised when trying to load an input item and none available.

______________________________________________________________________

## exception `BusinessException`

**Source:** [`_exceptions.py:22`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L22)

An exception that can be raised to release an input work item with a BUSINESS exception type.

### method `__init__`

**Source:** [`_exceptions.py:11`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L11)

```python
__init__(message: Optional[str] = None, code: Optional[str] = None)
```

______________________________________________________________________

## exception `ApplicationException`

**Source:** [`_exceptions.py:29`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L29)

An exception that can be raised to release an input work item with an APPLICATION exception type.

### method `__init__`

**Source:** [`_exceptions.py:11`](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L11)

```python
__init__(message: Optional[str] = None, code: Optional[str] = None)
```
