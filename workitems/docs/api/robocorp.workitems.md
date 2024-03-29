<!-- markdownlint-disable -->

# module `robocorp.workitems`

# Variables

- **inputs**
- **outputs**

# Functions

______________________________________________________________________

# Class `Input`

Container for an input work item.

An input work item can contain arbitrary JSON data in the `payload` section, and optionally attached files that are stored in Control Room.

Each step run of a process in Control Room has at least one input work item associated with it, but the step's input queue can have multiple input items in it.

There can only be one input work item reserved at a time. To reserve the next item, the current item needs to be released as either passed or failed.

### `__init__`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L222)

```python
__init__(adapter: BaseAdapter, item_id: str)
```

## Properties

- `exception`

Current work item exception if any.

- `files`

Names of attached files.

- `id`

Current ID for work item.

- `outputs`

Child output work items.

- `parent_id`

Current parent work item ID (output only).

- `payload`

Current JSON payload.

- `released`

Is the current item released.

- `saved`

Is the current item saved.

- `state`

Current release state.

## Methods

______________________________________________________________________

### `add_file`

Attach a file from the local machine to the work item.

Note: Files are not uploaded until the item is saved.

**Args:**

- <b>`path`</b>:  Path to attached file
- <b>`name`</b>:  Custom name for file in work item

**Returns:**
Resolved path to added file

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L118)

```python
add_file(path: Union[Path, str], name: Optional[str] = None) → Path
```

______________________________________________________________________

### `add_files`

Attach files from the local machine to the work item that match the given pattern.

Note: Files are not uploaded until the item is saved.

**Args:**

- <b>`pattern`</b>:  Glob pattern for attached file paths

**Returns:**
List of added paths

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L145)

```python
add_files(pattern: Union[Path, str]) → list[Path]
```

______________________________________________________________________

### `create_output`

Create an output work item that is a child of this item.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L440)

```python
create_output() → Output
```

______________________________________________________________________

### `done`

Mark this work item as done, and release it.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L448)

```python
done()
```

______________________________________________________________________

### `email`

Parse an email attachment from the work item.

**Args:**

- <b>`html`</b>:  Parse the HTML content into the `html` attribute
- <b>`encoding`</b>:  Text encoding of the email
- <b>`ignore_errors`</b>:  Ignore possible parsing errors from Control Room

**Returns:**
An email container with metadata and content

**Raises:**

- <b>`ValueError`</b>:  No email attached or content is malformed

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L294)

```python
email(html=True, encoding='utf-8', ignore_errors=False) → Optional[Email]
```

______________________________________________________________________

### `fail`

Mark this work item as failed, and release it.

**Args:**

- <b>`exception_type`</b>:  Type of failure (APPLICATION or BUSINESS)
- <b>`code`</b>:  Custom error code for the failure
- <b>`message`</b>:  Human-readable error message

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L459)

```python
fail(
    exception_type: Union[ExceptionType, str] = <ExceptionType.APPLICATION: 'APPLICATION'>,
    code: Optional[str] = None,
    message: Optional[str] = None
)
```

______________________________________________________________________

### `get_file`

Download file with given name.

If a `path` is not defined, uses the Robot root or current working directory.

**Args:**

- <b>`name`</b>:  Name of file
- <b>`path`</b>:  Path to created file

**Returns:**
Path to created file

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L372)

```python
get_file(name: str, path: Optional[Path, str] = None) → Path
```

______________________________________________________________________

### `get_files`

Download all files attached to this work item that match the given pattern.

If a `path` is not defined, uses the Robot root or current working directory.

**Args:**

- <b>`pattern`</b>:  Glob pattern for file names
- <b>`path`</b>:  Directory to store files in

**Returns:**
List of created file paths

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L402)

```python
get_files(pattern: str, path: Optional[Path, str] = None) → list[Path]
```

______________________________________________________________________

### `load`

Load work item payload and file listing from Control Room.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L72)

```python
load() → None
```

______________________________________________________________________

### `remove_file`

Remove attached file with given name.

Note: Files are not removed from Control Room until the item is saved.

**Args:**

- <b>`name`</b>:  Name of file
- <b>`missing_ok`</b>:  Do nothing if given file does not exist

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L167)

```python
remove_file(name: str, missing_ok: bool = False)
```

______________________________________________________________________

### `remove_files`

Remove attached files that match the given pattern.

Note: Files are not removed from Control Room until the item is saved.

**Args:**

- <b>`pattern`</b>:  Glob pattern for file names

**Returns:**
List of matched names

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L186)

```python
remove_files(pattern: str) → list[str]
```

______________________________________________________________________

### `save`

Save the current input work item.

Updates the work item payload and adds/removes all pending files.

**Note:** Modifying input work items is not recommended, as it will make traceability after execution difficult, and potentially makethe process behave in unexpected ways.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L283)

```python
save()
```

______________________________________________________________________

# Class `Inputs`

Inputs represents the input queue of work items.

It can be used to reserve and release items from the queue, and iterate over them.

## Properties

- `current`

The current reserved input item.

- `released`

A list of inputs reserved and released during the lifetime of the library.

## Methods

______________________________________________________________________

### `reserve`

Reserve a new input work item.

There can only be one item reserved at a time.

**Returns:**
Input work item

**Raises:**

- <b>`RuntimeError`</b>:  An input work item is already reservedworkitems.EmptyQueue: There are no further items in the queue

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/__init__.py#L99)

```python
reserve() → Input
```

______________________________________________________________________

# Class `Output`

Container for an output work item.

Created output items are added to an output queue, and released to the next step of a process when the current run ends.

Note: An output item always has an input item as a parent, which is used for traceability in a work item's history.

### `__init__`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L528)

```python
__init__(adapter: BaseAdapter, parent_id: str)
```

## Properties

- `files`

Names of attached files.

- `id`

Current ID for work item.

- `parent_id`

Current parent work item ID (output only).

- `payload`

Current JSON payload.

- `saved`

Is the current item saved.

## Methods

______________________________________________________________________

### `add_file`

Attach a file from the local machine to the work item.

Note: Files are not uploaded until the item is saved.

**Args:**

- <b>`path`</b>:  Path to attached file
- <b>`name`</b>:  Custom name for file in work item

**Returns:**
Resolved path to added file

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L118)

```python
add_file(path: Union[Path, str], name: Optional[str] = None) → Path
```

______________________________________________________________________

### `add_files`

Attach files from the local machine to the work item that match the given pattern.

Note: Files are not uploaded until the item is saved.

**Args:**

- <b>`pattern`</b>:  Glob pattern for attached file paths

**Returns:**
List of added paths

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L145)

```python
add_files(pattern: Union[Path, str]) → list[Path]
```

______________________________________________________________________

### `load`

Load work item payload and file listing from Control Room.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L72)

```python
load() → None
```

______________________________________________________________________

### `remove_file`

Remove attached file with given name.

Note: Files are not removed from Control Room until the item is saved.

**Args:**

- <b>`name`</b>:  Name of file
- <b>`missing_ok`</b>:  Do nothing if given file does not exist

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L167)

```python
remove_file(name: str, missing_ok: bool = False)
```

______________________________________________________________________

### `remove_files`

Remove attached files that match the given pattern.

Note: Files are not removed from Control Room until the item is saved.

**Args:**

- <b>`pattern`</b>:  Glob pattern for file names

**Returns:**
List of matched names

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L186)

```python
remove_files(pattern: str) → list[str]
```

______________________________________________________________________

### `save`

Save the current work item.

Updates the work item payload and adds/removes all pending files.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_workitem.py#L82)

```python
save()
```

______________________________________________________________________

# Class `Outputs`

Outputs represents the output queue of work items.

It can be used to create outputs and inspect the items created during the execution.

## Properties

- `last`

The most recently created output work item, or `None`.

## Methods

______________________________________________________________________

### `create`

Create a new output work item, which can have both a JSON payload and attached files.

Creating an output item requires an input to be currently reserved.

**Args:**

- <b>`payload`</b>:  JSON serializable data (dict, list, scalar, etc.)
- <b>`files`</b>:  List of paths to files or glob pattern
- <b>`save`</b>:  Immediately save item after creation

**Raises:**

- <b>`RuntimeError`</b>:  No input work item reserved

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/__init__.py#L140)

```python
create(
    payload: Optional[dict[str, Any], list[Any], str, int, float, bool] = None,
    files: Optional[Path, str, list[Union[Path, str]]] = None,
    save: bool = True
) → Output
```

# Exceptions

______________________________________________________________________

## `ApplicationException`

An exception that can be raised to release an input work item with an APPLICATION exception type.

### `__init__`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L11)

```python
__init__(message: Optional[str] = None, code: Optional[str] = None)
```

______________________________________________________________________

## `BusinessException`

An exception that can be raised to release an input work item with a BUSINESS exception type.

### `__init__`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/workitems/src/robocorp/workitems/_exceptions.py#L11)

```python
__init__(message: Optional[str] = None, code: Optional[str] = None)
```

______________________________________________________________________

## `EmptyQueue`

Raised when trying to load an input item and none available.

# Enums

______________________________________________________________________

## `ExceptionType`

Failed work item error type.

### Values

- **BUSINESS** = BUSINESS
- **APPLICATION** = APPLICATION

______________________________________________________________________

## `State`

Work item state, after release.

### Values

- **DONE** = COMPLETED
- **FAILED** = FAILED
