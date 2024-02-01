# Locators

One of the key concepts in the library are locators. A locator is a string which
identifies how to reach a given element to interact with. This string can have
multiple entries separated by spaces such as:

`<property_name>:"<property value>" <property_name>:"<property value>"`

Note: if the `<property value>` itself doesn't have spaces the `"` is not needed.

It's also possible to consider the parent/child hierarchy so that multiple
matches are done when using `>`. Example: `name:Calculator > class:TextBlock`.

Also, it's possible to use `or` constructs to create more advanced matches.
Example: `(name:0 or name:Zero) and class:Button`.
Note: `>` must always be top-level and may not appear inside an `or`.

The property names available for matching are:

- `name`: identifies a target window/control by its `name`. Example: `name:"My Window"`.

- `regex`: identifies a target window/control by its `name` matching using a regexp. Example: `regex:".*Calc.*"`.

- `subname` identifies a target window/control by its `name` matching using the `in` operator. Example: `subname:cal"`.

- `class`: identifies a target window/control by its `class`. Example: `class:Button`, `class:TextBlock`.

- `control` (may also be used as `type`): identifies a target window/control by its `type`. Example: `control:ButtonControl`, `type:ButtonControl`.

- `id` (may also be used as `automationid`): identifies a target window/control by its `automation id`. Example: `id:"open button"`.

- `executable`: identifies a target window by its executable name (may be the full path or just basename). Example: `executable:notepad.exe`)

- `handle`: the target window handle. Example: `handle:21345`.

- `path`: identifies a target element by its index-based path traversal from the parent. Example `path:2|3|8|2`.

- `depth`: identifies a target element by its depth from the parent. Example `depth:2`.

It's also possible to get an element and then go deeper in the structure to have the
same result.

i.e.: Using:

```python
from robocorp import windows
windows.find_window('name:Calculator').find('path:2|3|1').click()
```

is the same as:

```python
from robocorp import windows
windows.find_window('name:Calculator').find('path:2 > path:3|1').click()
```

In general the recommended approach is getting the top-level window of interest
with `windows.find_window` and then getting sub-elements as needed (and if 
multiple elements have the same parent, first finding the parent and then getting
children elements from that parent for faster access).

Note: when querying the information, APIs may have a `search_depth` or `max_depth` 
parameter which can be specified to determine up to which depth a given element 
may be found. It's not recommended to have a big depth value as bigger depths
mean that more items have to be traversed to find an element which can make 
such searches slower (so, more queries with a shalower depth is recommended 
over less queries with a bigger depth).
