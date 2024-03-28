`robocop-windows` is a library that can be used for Windows desktop automation.

The basic idea of the library is to enable windows and controls to be found by leveraging `locators` (i.e., strings that identify how to reach some window or control) and then interacting with such elements.

There are three fundamental abstractions in the library:

- `Desktop`: enables finding `WindowElement and interacting directly with the desktop (so, actions which aren't tied to a Window or Control can be used directly through the `Desktop`).
- `WindowElement`: enables finding `ControlElement's and interacting with a Window.
- `ControlElement`: enables finding child `ControlElement's and interacting with a specific Control.

Note: The library itself always creates these classes and are not expected
to be subclassed or instanced directly.

## Usage

![`robocorp-windows`](https://img.shields.io/pypi/v/robocorp-windows?label=robocorp-windows)

> 👉 Check that you have added the dependency in your configuration; this library is not a part of the `robocop` -package.
> - _conda.yaml_ for automation [Task Packages](https://robocorp.com/docs/robot-structure)
> - _action-package.yaml_ for automation Action Packages
> - _requirements.txt_, _pyproject.toml_ etc. for the rest


The library concepts revolve around the idea that the window of interest will be 
initially found using `find_window` and then, with that window reference, other
controls can be queried and interacted with (for clicking, entering text, etc).

Below is an example using the Windows calculator:

"`python
from robocorp import windows

# Get the calculator window
calc = windows.find_window("name:Calculator")

# Press button 0 (the locator is dependent on the Windows version).
button0 = calc.find('(name:Zero or name:0) and class:Button')
button0.click()

# Clear the calculator (the locator is dependent on the Windows version).
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

This library uses semantic versioning, so a new major version will be published when breaking changes are done, and the changelog should contain guidance on what was changed. 

Be aware that modules starting with an underscore `_` in `robocorp.windows` are not considered part of the public API and should not be imported directly (so only objects/classes reached from the `robocorp.windows` namespace should be used -- if access to some other method/class is needed, please create a feature request to address it).
