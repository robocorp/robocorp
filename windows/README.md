# robocorp-windows

The **robocop-windows** package brings a library that can be used for Windows desktop automation.

The basic idea of the library is to enable windows and controls to be found by leveraging "locators" (strings that identify how to reach some window or control), then interacting with such elements.

There are three fundamental abstractions in the library:

- `Desktop`: enables finding `WindowElement`s and interacting directly with the desktop, like opening or closing apps. These actions aren't tied to a specific _Window_ or _Control_.
- `WindowElement`: enables finding direct `ControlElement`s and interacting with a specific _Window_.
- `ControlElement`: enables finding child `ControlElement`s and interacting with a specific _Control_.

> Note: The library itself always creates these classes which are not expected to be subclassed or instanced directly.

## Usage

[![`robocorp-windows`](https://img.shields.io/pypi/v/robocorp-windows?label=robocorp-windows)](https://pypi.org/project/robocorp-windows/)

> 👉 Check that you have added the dependency in your configuration; this library is not part of the [**robocorp**](https://pypi.org/project/robocorp/) bundle.
> - _conda.yaml_ for automation [Task Packages](https://robocorp.com/docs/robot-structure)
> - _package.yaml_ for automation Action Packages
> - _requirements.txt_, _pyproject.toml_, _setup.py|cfg_ etc. for the rest

The library concepts revolve around the idea that the window of interest will be initially found using `find_window` and then, with that window reference, other controls can be queried and interacted with (for clicking, entering text etc.).

Below is an example using the Windows' Calculator app:

```python
from robocorp import windows

# Get the Calculator window.
calc = windows.find_window("name:Calculator")

# Press button "0" (the locator may vary based on the Windows version).
button0 = calc.find("(name:0 or name:num0Button) and type:Button")
button0.click()

# Clear the Calculator (the locator may vary based on the Windows version).
calc.click("id:clearEntryButton or name:Clear")

# Send the keys directly to the Calculator by typing them from the keyboard.
calc.send_keys(keys="96+4=")
```

## Guides

- [Quickstart](https://github.com/robocorp/robocorp/blob/master/windows/docs/guides/00-quickstart.md)
- [Understanding Locators](https://github.com/robocorp/robocorp/blob/master/windows/docs/guides/01-locators.md)
- [Building Locators using the builtin inspector](https://github.com/robocorp/robocorp/blob/master/windows/docs/guides/02-locator-inspecting.md)
- [Special keys](https://github.com/robocorp/robocorp/blob/master/windows/docs/guides/03-special-keys.md)

## API Reference

Explore our [API](https://github.com/robocorp/robocorp/blob/master/windows/docs/api/README.md) for extensive documentation.

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/windows/docs/CHANGELOG.md).
