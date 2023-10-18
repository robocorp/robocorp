`robocorp-windows` is a library which can be used for Windows desktop automation.

The basic idea of the library is enabling windows and controls to be found
by leveraging `locators` (i.e.: strings which identify how to reach some
window or control) and then interacting with such elements (see the related
guide entry for more details).

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
