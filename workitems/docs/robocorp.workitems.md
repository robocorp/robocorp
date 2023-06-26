<!-- markdownlint-disable -->

<a href="../../workitems/src/robocorp/workitems/__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.workitems`




**Global Variables**
---------------
- **version_info**
- **inputs**
- **outputs**


---

<a href="../../workitems/src/robocorp/workitems/__init__.py#L65"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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

<a href="../../workitems/src/robocorp/workitems/__init__.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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

<a href="../../workitems/src/robocorp/workitems/__init__.py#L111"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `Outputs`
Outputs represents the output queue of work items. 

It can be used to create outputs and inspect the items created during the execution. 


---

#### <kbd>property</kbd> last

The most recently created output work item, or `None`. 



---

<a href="../../workitems/src/robocorp/workitems/__init__.py#L137"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
