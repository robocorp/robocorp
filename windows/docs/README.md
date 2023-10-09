`robocorp-windows` is a library which can be used for Windows desktop automation.

The basic idea of the library is enabling windows and controls to be found
by leveraging `locators` (i.e.: strings which identify how to reach some
window or control) and then interacting with such elements.

There are 3 basic abstractions in the library:

- `Desktop`: enables finding `WindowElement`s and interacting directly with the 
  desktop (so, actions which aren't tied to a Window or Control can be used directly
  through the `Desktop`).
- `WindowElement`: enables finding `ControlElement`s and interacting with a Window.
- `ControlElement`: enables finding child `ControlElement`s and interacting with a specific Control.

Note: these classes are always created by the library itself and are not expected
to be subclassed or instanced directly.

Note: This library uses semantic versioning, so, when a breaking change is done
a new major version is published, but beware that modules starting with an 
underscore `_` in `robocorp.windows` are not considered
part of the public API and should not be imported directly (so, only objects/classes
reached from the `robocorp.windows` namespace should be used -- if access to some
other method/class is needed, please create a feature request to address it).

Locators
-----------

One of the key concepts in the library are locators. A locator is a string which
identifies how to reach a given element to interact with. This string can have
multiple entries separated by spaces such as:

`<property_name>:"<property value>" <property_name>:"<property value>"`

Note: if the `<property value>` itself doesn't have spaces the `"` is not needed.

The property names available for matching are:

`name`: identifies a target window/control by its `name`. Example: `name:"My Window"`.
`regex`: identifies a target window/control by its `name` matching using a regexp. Example: `regex:".*Calc.*"`.
`subname` identifies a target window/control by its `name` matching using the `in` operator. Example: `subname:cal"`.
`class`: identifies a target window/control by its `class`. Example: `control:Button`, `control:TextBlock`.
`control` (may also be used as `class`): identifies a target window/control by its `type`. Example: `control:ButtonControl`, `control:ButtonControl`.
`id` (may also be used as `automationid`): identifies a target window/control by its `automation id`. Example: `id:"open button"`.
`executable`: identifies a target window by its executable name (may be the full path or just basename). Example: `executable:notepad.exe`)
`handle`: the target window handle. Example: `handle:21345`.
`path`: identifies a target element by its index-based path traversal from the parent. Example `path:2|3|8|2`.

Note: it's possible to consider the parent/child hierarchy so that multiple
matches are done when using `>`. Example: `name:Calculator > class:TextBlock`.

It's also possible to get an element and then go deeper in the structure to have the
same result.

i.e.: Using:

```
from robocorp import windows
windows.find_window('name:Calculator').find('path:2|3|1').click()
```

is the same as:

```
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
mean that more items have to be traversed to
find an element which can make such searches slower (so, more queries with a
shalower depth is recommended over less queries with a bigger depth).

