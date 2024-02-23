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

## Usage

![`robocorp-windows`](https://img.shields.io/pypi/v/robocorp-windows?label=robocorp-windows)

> 👉 Check that you have added the dependency in your configuration, this library is not apart of the `robocorp` -package.
> - _conda.yaml_ for an automation [Task Packages](https://robocorp.com/docs/robot-structure)
> - _action-package.yaml_ for an automation Action Packages
> - _requirements.txt_, _pyproject.toml_ etc. for the rest


The library concepts revolve around the idea that the window of interest will be 
initially found using `find_window` and then, with that window reference, other
controls can be queried and interacted with (for clicking, entering text, etc).

Below is an example using the windows calculator:

```python
from robocorp import windows

# Get the calculator window
calc = windows.find_window("name:Calculator")

# Press button 0 (the locator is dependent on the windows version).
button0 = calc.find('(name:Zero or name:0) and class:Button')
button0.click()

# Clear the calculator (the locator is dependent on the windows version).
calc.click("id:clearButton or name:Clear")

# Send the keys directly to the calculator
calc.send_keys(keys="96+4=")
```

## Guides

- [Understanding Locators](https://github.com/robocorp/robocorp/blob/master/windows/docs/guides/00-locators.md)
- [Building Locators using the builtin inspector](https://github.com/robocorp/robocorp/blob/master/windows/docs/guides/01-locator-inspecting.md)
- [Special keys](https://github.com/robocorp/robocorp/blob/master/windows/docs/guides/02-special-keys.md)


## API Reference

Information on specific functions or classes: [robocorp.windows](https://github.com/robocorp/robocorp/blob/master/windows/docs/api/robocorp.windows.md)

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/windows/docs/CHANGELOG.md).

## Versioning

This library uses semantic versioning, so, when a breaking change is done
a new major version is published, but beware that modules starting with an 
underscore `_` in `robocorp.windows` are not considered
part of the public API and should not be imported directly (so, only objects/classes
reached from the `robocorp.windows` namespace should be used -- if access to some
other method/class is needed, please create a feature request to address it).
