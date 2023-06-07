<!-- markdownlint-disable -->

<a href="../../workitems/src/robocorp/workitems/__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.workitems`
A library for interacting with Control Room work items. 

Work items are used for managing data that go through multiple steps and tasks inside a process. Each step of a process receives input work items from the previous step, and creates output work items for the next step. 

**Installation** 

The library can be installed from pip:
``` 

     pip install robocorp-workitems 

```
**Usage** 

```python
from robocorp import workitems

def read_inputs_and_create_outputs():
     for item in workitems.inputs:
         print("Received payload:", item.payload)
         workitems.outputs.create(payload={"key": "value"})
``` 

**Work item structure** 

A work item's data payload is JSON and allows storing anything that is serializable. By default the payload is a mapping of key-value pairs. 

In addition to the payload section, a work item can also contain files, which are stored within Robocorp Control Room. Adding and using files with work items requires no additional setup from the user. 

**Loading inputs** 

The library automatically loads the first input work item, if the library input argument ``autoload`` is truthy (default). 

After an input has been loaded its payload and files can be accessed through corresponding keywords, and optionally these values can be modified. 

**Email triggering** 

Since a process can be started in Control Room by sending an e-mail, a body in Text/JSON/YAML/HTML format can be sent as well and this gets attached to the input work item with the ``rawEmail`` payload variable. This library automatically parses the content of it and saves into ``parsedEmail`` the dictionary transformation of the original e-mail. 

If "Parse email" Control Room configuration option is enabled (recommended), then your e-mail is automatically parsed in the work item under the ``email`` payload variable, which is a dictionary containing a ``body`` holding the final parsed form of the interpreted e-mail body. The payload variable ``parsedEmail`` is still available for backwards compatibility reasons and holds the very same body inside the ``parsedEmail[Body]``. 

E-mail attachments will be added into the work item as files. Read more on: https://robocorp.com/docs/control-room/attended-or-unattended/email-trigger 



**Example:**
 

After starting the process by sending an e-mail with a body like: 

.. code-block:: json 

 {  "message": "Hello world!"  } 

The robot can use the parsed e-mail body's dictionary: 

.. code-block:: robotframework 

 *** Tasks ***  Using Prased Emails  ${mail} =    Get Work Item Variable    email  Set Work Item Variables    &{mail}[body]  ${message} =     Get Work Item Variable     message  Log    ${message}    # will print "Hello world!" 

The behaviour can be disabled by loading the library with ``auto_parse_email=${None}`` or altered by providing to it a dictionary with one "key: value" where the key is usually "email.text" (deprecated "rawEmail", the variable set by Control Room, which acts as source for the parsed (deprecated raw) e-mail data) and the value can be "email.body" (deprecated "parsedEmail", where the parsed e-mail data gets stored into), value which can be customized and retrieved with ``Get Work Item Variable``. 

**Creating outputs** 

It's possible to create multiple new work items as an output from a task. With the keyword ``Create Output Work Item`` a new empty item is created as a child for the currently loaded input. 

All created output items are sent into the input queue of the next step in the process. 

**Active work item** 

Keywords that read or write from a work item always operate on the currently active work item. Usually that is the input item that has been automatically loaded when the execution started, but the currently active item is changed whenever the keywords ``Create Output Work Item`` or ``Get Input Work Item`` are called. It's also possible to change the active item manually with the keyword ``Set current work item``. 

**Saving changes** 

While a work item is loaded automatically when a suite starts, changes are not automatically reflected back to the source. The work item will be modified locally and then saved when the keyword ``Save Work Item`` is called. This also applies to created output work items. 

It is recommended to defer saves until all changes have been made to prevent leaving work items in a half-modified state in case of failures. 

**Local Development** 

While Control Room is the default implementation, it can also be replaced with a custom adapter. The selection is based on either the ``default_adapter`` argument for the library, or the ``RPA_WORKITEMS_ADAPTER`` environment variable. The library has a built-in alternative adapter called FileAdapter for storing work items to disk. 

The FileAdapter uses a local JSON file for input work items. It's a list of work items, each of which has a data payload and files. 

An example of a local file with one work item: 

.. code-block:: json 

 [  {  "payload": {  "variable1": "a-string-value",  "variable2": ["a", "list", "value"]  },  "files": {  "file1": "path/to/file.ext"  }  }  ] 

Output work items (if any) are saved to an adjacent file with the same name, but with the extension ``.output.json``. You can specify through the "RPA_OUTPUT_WORKITEM_PATH" env var a different path and name for this file. 

**Simulating the Cloud with Robocorp Code VSCode Extension** 

If you are developing in VSCode with the `Robocorp Code extension`_, you can utilize the built in local development features described in the `Developing with work items locally`_ section of the `Using work items`_ development guide. 

.. _Robocorp Code extension: https://robocorp.com/docs/setup/development-environment#visual-studio-code-with-robocorp-extensions .. _Developing with work items locally: https://robocorp.com/docs/development-guide/control-room/work-items#developing-with-work-items-locally .. _Using work items: https://robocorp.com/docs/development-guide/control-room/work-items 

**Global Variables**
---------------
- **version_info**
- **inputs**
- **outputs**


---

<a href="../../workitems/src/robocorp/workitems/__init__.py#L219"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `Inputs`
Inputs represents the input queue of work items. 

It can be used to reserve and release items from the queue, and iterate over them. 



**Example:**
 Multiple items can behandled by iterating over this class:
``` 

         for item in inputs:              handle_item(item.payload) 


---

#### <kbd>property</kbd> current

The current reserved input item. 

---

#### <kbd>property</kbd> released

A list of inputs reserved and released during the lifetime of the library. 



---

<a href="../../workitems/src/robocorp/workitems/__init__.py#L256"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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

<a href="../../workitems/src/robocorp/workitems/__init__.py#L271"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `Outputs`
Outputs represents the output queue of work items. It can be used to create outputs and inspect the items created during the execution. 



**Example:**
 The class can be used to create outputs:
``` 

         outputs.create({"key": "value"}) 


---

#### <kbd>property</kbd> last

The most recently created output work item, or `None`. 



---

<a href="../../workitems/src/robocorp/workitems/__init__.py#L304"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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
