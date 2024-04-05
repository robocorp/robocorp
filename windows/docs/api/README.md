<!-- markdownlint-disable -->

# API Overview

## Modules

- [`robocorp.windows`](./robocorp.windows.md#module-robocorpwindows): Module used to interact with native widgets on the Windows OS through UI Automation.
- [`robocorp.windows.protocols`](./robocorp.windows.protocols.md#module-robocorpwindowsprotocols)

## Classes

- [`_errors.ActionNotPossible`](./robocorp.windows._errors.md#class-actionnotpossible): Action is not possible for the given Control.
- [`_control_element.ControlElement`](./robocorp.windows._control_element.md#class-controlelement): Class used to interact with a control.
- [`_desktop.Desktop`](./robocorp.windows._desktop.md#class-desktop): The desktop is the control, containing other top-level windows.
- [`_errors.ElementDisposed`](./robocorp.windows._errors.md#class-elementdisposed): The existing element was disposed and is no longer available.
- [`_errors.ElementNotFound`](./robocorp.windows._errors.md#class-elementnotfound): No matching elements were found.
- [`_errors.InvalidLocatorError`](./robocorp.windows._errors.md#class-invalidlocatorerror): The locator specified is invalid.
- [`_errors.InvalidStrategyDuplicated`](./robocorp.windows._errors.md#class-invalidstrategyduplicated): A given strategy is defined more than once in the same level.
- [`builtins.str`](./builtins.md#class-str): str(object='') -> str
- [`_errors.ParseError`](./robocorp.windows._errors.md#class-parseerror): The locator specified is invalid because it was not possible to parse it properly.
- [`_window_element.WindowElement`](./robocorp.windows._window_element.md#class-windowelement): Class used to interact with a window.

## Functions

- [`windows.config`](./robocorp.windows.md#function-config): Provides an instance to configure the basic settings such as
- [`windows.desktop`](./robocorp.windows.md#function-desktop): Provides the desktop element (which is the root control containing
- [`windows.find_window`](./robocorp.windows.md#function-find_window): Finds the first window matching the passed locator.
- [`windows.find_windows`](./robocorp.windows.md#function-find_windows): Finds all windows matching the given locator.
- [`windows.get_icon_from_file`](./robocorp.windows.md#function-get_icon_from_file): Provides the icon stored in the file of the given path.
- [`windows.wait_for_condition`](./robocorp.windows.md#function-wait_for_condition): A helper function to wait for some condition.
