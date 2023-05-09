<!-- markdownlint-disable -->

<a href="../../workitems/src/robocorp/workitems/workitem.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `robocorp.workitems.workitem`






---

<a href="../../workitems/src/robocorp/workitems/workitem.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `State`
Work item state. (set when released) 





---

<a href="../../workitems/src/robocorp/workitems/workitem.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Error`
Failed work item error type. 





---

<a href="../../workitems/src/robocorp/workitems/workitem.py#L27"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `WorkItem`
Base class for input and output work items. 



**Args:**
 
 - <b>`adapter`</b>:    Adapter instance 
 - <b>`item_id`</b>:    Work item ID (optional) 
 - <b>`parent_id`</b>:  Parent work item's ID (optional) 

<a href="../../workitems/src/robocorp/workitems/workitem.py#L37"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(adapter, item_id=None, parent_id=None)
```






---

#### <kbd>property</kbd> files

List of filenames, including local files pending upload and excluding files pending removal. 

---

#### <kbd>property</kbd> is_dirty

Check if work item has unsaved changes. 

---

#### <kbd>property</kbd> payload





---

#### <kbd>property</kbd> released







---

<a href="../../workitems/src/robocorp/workitems/workitem.py#L163"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `add_file`

```python
add_file(path, name=None)
```

Add file to current work item. Does not upload until ``save()`` is called. 

:param path: Path to file to upload :param name: Name of file in work item. If not given,  name of file on disk is used. 

---

<a href="../../workitems/src/robocorp/workitems/workitem.py#L211"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `done`

```python
done()
```

Mark item status as DONE. 

---

<a href="../../workitems/src/robocorp/workitems/workitem.py#L220"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `fail`

```python
fail(
    exception_type: Optional[Error, str] = None,
    code: Optional[str] = None,
    message: Optional[str] = None
)
```





---

<a href="../../workitems/src/robocorp/workitems/workitem.py#L123"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_file`

```python
get_file(name, path=None) → str
```

Load an attached file and store it on the local filesystem. 

:param name: Name of attached file :param path: Destination path. Default to current working directory. :returns:    Path to created file 

---

<a href="../../workitems/src/robocorp/workitems/workitem.py#L150"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_files`

```python
get_files(pattern, dirname=None) → List[str]
```





---

<a href="../../workitems/src/robocorp/workitems/workitem.py#L90"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `load`

```python
load()
```

Load data payload and list of files. 

---

<a href="../../workitems/src/robocorp/workitems/workitem.py#L187"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_file`

```python
remove_file(name, missing_ok=True)
```

Remove file from current work item. Change is not applied until ``save()`` is called. 

:param name: Name of attached file 

---

<a href="../../workitems/src/robocorp/workitems/workitem.py#L99"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save`

```python
save()
```

Save data payload and attach/remove files. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
