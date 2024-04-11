<!-- markdownlint-disable -->

# module `robocorp.windows`

Module used to interact with native widgets on the Windows OS through UI Automation.

This library can be made available by pinning [![](https://img.shields.io/pypi/v/robocorp-windows?label=robocorp-windows)](https://pypi.org/project/robocorp-windows/) in your dependencies' configuration.

# Functions

______________________________________________________________________

## `get_icon_from_file`

Provides the icon stored in the file of the given path.

**Returns:**
A PIL image with the icon image or None if it was not possible to load it.

**Example:**

```python
# Get icon from file and convert it to a base64 string
from robocorp import windows
from io import BytesIO

img = windows.get_icon_from_file('c:/temp/my.exe')
buffered = BytesIO()
img.save(buffered, format="PNG")
image_string = base64.b64encode(buffered.getvalue()).decode()
```

**Example:**

```python
# Get icon from file and save it in the filesystem
from robocorp import windows

img = windows.get_icon_from_file('c:/temp/my.exe')

img.save("c:/temp/my.png", format="PNG")
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/__init__.py#L36)

```python
get_icon_from_file(path: str) → Optional[ForwardRef('Image')]
```

______________________________________________________________________

## `desktop`

Provides the desktop element (which is the root control containing top-level windows).

The elements provided by robocorp-windows are organized as: Desktop (root control)WindowElement (top-level windows)ControlElement (controls inside a window)

**Returns:**
The Desktop element.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/__init__.py#L84)

```python
desktop() → Desktop
```

______________________________________________________________________

## `config`

Provides an instance to configure the basic settings such as the default timeout, whether to simulate mouse movements, showing verbose errors on failures, screenshot on error (when running with robocorp-tasks), etc.

**Returns:**
Config object to be used to configure the settings.

**Example:**

```
from robocorp import windows
config = windows.config()
config.verbose_errors = True
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/__init__.py#L100)

```python
config() → Config
```

______________________________________________________________________

## `find_window`

Finds the first window matching the passed locator.

**Args:**

- <b>`locator`</b>:  This is the locator which should be used to find the window.

- <b>`search_depth`</b>:  The search depth to find the window (by default == 1, meaning that only top-level windows will be found).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used.

- <b>`wait_time`</b>:  The time to wait after finding the window. If not passed the default value found in the config is used.

- <b>`foreground`</b>:  Whether the found window should be made top-level when found.

- <b>`raise_error`</b>:  Do not raise and return `None` when this is set to `True` and such a window isn't found.

**Returns:**
The `WindowElement` which should be used to interact with the window.

**Example:**

```python
window = find_window('Calculator')
window = find_window('name:Calculator')
window = find_window('subname:Notepad')
window = find_window('regex:.*Notepad')
window = find_window('executable:Spotify.exe')
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/__init__.py#L157)

```python
find_window(
    locator: str,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None,
    foreground: bool = True,
    raise_error: bool = True
) → Optional[ForwardRef('WindowElement')]
```

______________________________________________________________________

## `find_windows`

Finds all windows matching the given locator.

**Args:**

- <b>`locator`</b>:  The locator which should be used to find windows (if not given, all windows are returned).

- <b>`search_depth`</b>:  The search depth to be used to find windows (by default equals 1, meaning that only top-level windows will be found).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `wait_for_window` is True.

- <b>`wait_for_window`</b>:  Defines whether the search should keep on searching until a window with the given locator is found (note that if True and no window was found a ElementNotFound is raised).

**Returns:**
The `WindowElement`s which should be used to interact with the window.

**Example:**

```python
window = find_windows('Calculator')
window = find_windows('name:Calculator')
window = find_windows('subname:Notepad')
window = find_windows('regex:.*Notepad')
window = find_windows('executable:Spotify.exe')
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/__init__.py#L206)

```python
find_windows(
    locator: str = 'regex:.*',
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_for_window: bool = False
) → List[ForwardRef('WindowElement')]
```

______________________________________________________________________

## `wait_for_condition`

A helper function to wait for some condition.

**Args:**

- <b>`condition`</b>:  The condition to be waited for.
- <b>`timeout`</b>:  The time to wait for the condition.
- <b>`msg`</b>:  An optional message to be shown in the exception if the condition is not satisfied.

**Raises:**

- <b>`TimeoutError`</b>:  If the condition was not satisfied in the given timeout.

**Example:**

```python
from robocorp import windows

calc_window = windows.find_window("name:Calculator")
calc_window.click("Close Calculator")
windows.wait_for_condition(calc_window.is_disposed)
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/__init__.py#L250)

```python
wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 8.0,
    msg: Optional[Callable[[], str]] = None
)
```

______________________________________________________________________

# Class `ControlElement`

Class used to interact with a control.

### `__init__`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L79)

```python
__init__(wrapped: '_UIAutomationControlWrapper')
```

## Properties

- `automation_id`

**Returns:**
The automation id of the underlying control wrapped in this class (matches the locator `automationid` or `id`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `bottom`

**Returns:**
The bottom bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `class_name`

**Returns:**
The class name of the underlying control wrapped in this class (matches the locator `class`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `control_type`

**Returns:**
The control type of the underlying control wrapped in this class (matches the locator `control` or `type`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `handle`

**Returns:**
The internal native window handle from the control wrapped in this class.

- `height`

**Returns:**
The height of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `left`

**Returns:**
The left bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `name`

**Returns:**
The name of the underlying control wrapped in this class (matches the locator `name`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `path`

Provides the relative path in which this element was found

Note: this is relative to the element which was used for the `find` or `find_window` and cannot be used as an absolute path to be used to find the control from the desktop.

- `rectangle`

**Returns:**
A tuple with (left, top, right, bottom) -- (all -1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `right`

**Returns:**
The right bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `top`

**Returns:**
The top bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `ui_automation_control`

Provides the Control actually wrapped by this ControlElement. Can be used as an escape hatch if some functionality is not directly covered by this class (in general this API should only be used if a better API isn't directly available in the ControlElement).

- `width`

**Returns:**
The width of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `xcenter`

**Returns:**
The x position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `ycenter`

**Returns:**
The y position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

## Methods

______________________________________________________________________

### `click`

Clicks an element using the mouse.

**Args:**

- <b>`locator`</b>:  If given the child element which matches this locator will be clicked.
- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).
- <b>`wait_time`</b>:  The time to wait after clicking the element. If not passed the default value found in the config is used.
- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is passed.

**Example:**

Click using a locator:

```python
from robocorp import windows
windows.find_window('Calculator').click('id:button1')
```

Click customizing wait time after the click:

```python
from robocorp import windows
calculator_window = windows.find_window('Calculator')
calculator_window.find('name:SendButton').click(wait_time=5.0)
```

Make an existing window foreground so that it can be clicked:

```python
window.foreground_window()
window.click('name:SendButton', wait_time=5.0)
```

**Returns:**
The clicked element.

**Note:**

> The element clicked must be visible in the screen, if it's hidden by some other window or control the click will not work.

**Raises:**

- <b>`ActionNotPossible`</b>:  if element does not allow the Click action.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L811)

```python
click(
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None
) → ControlElement
```

______________________________________________________________________

### `double_click`

Double-clicks an element using the mouse.

**Args:**

- <b>`locator`</b>:  If given the child element which matches this locator will be double-clicked.

- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is passed.

- <b>`wait_time`</b>:  The time to wait after double-clicking the element. If not passed the default value found in the config is used.

**Example:**

Double-click using a locator:

```python
from robocorp import windows
windows.find_window('Calculator').double_click('id:button1')
```

Click customizing wait time after the double-click:

```python
from robocorp import windows
calculator_window = windows.find_window('Calculator')
calculator_window.find('name:SendButton').double_click(wait_time=5.0)
```

Make an existing window foreground so that it can be double-clicked:

```python
window.foreground_window()
window.double_click('name:SendButton', wait_time=5.0)
```

**Returns:**
The clicked element.

**Note:**

> The element clicked must be visible in the screen, if it's hidden by some other window or control the double-click will not work.

**Raises:**

- <b>`ActionNotPossible`</b>:  if element does not allow the double-click action.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L872)

```python
double_click(
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None
) → ControlElement
```

______________________________________________________________________

### `find`

This method may be used to find a control in the descendants of this control.

The first matching element is returned.

**Args:**

- <b>`locator`</b>:  The locator to be used to search a child control.

- <b>`search_depth`</b>:  Up to which depth the hierarchy should be searched.

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used.

- <b>`raise_error`</b>:  Do not raise and return `None` when this is set to `True` and such a window isn't found.

**Raises:**
`ElementNotFound` if an element with the given locator could not befound.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L516)

```python
find(
    locator: str,
    search_depth: int = 8,
    timeout: Optional[float] = None,
    raise_error: bool = True
) → Optional[ForwardRef('ControlElement')]
```

______________________________________________________________________

### `find_many`

This method may be used to find multiple descendants of the current element matching the given locator.

**Args:**

- <b>`locator`</b>:  The locator that should be used to find elements.

- <b>`search_depth`</b>:  Up to which depth the tree will be traversed.

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `wait_for_element` is True.

- <b>`search_strategy`</b>:  The search strategy to be used to find elements. `siblings` means that after the first element is found, the tree traversal should be stopped and only sibling elements will be searched. `all` means that all the elements up to the given search depth will be searched.

- <b>`wait_for_element`</b>:  Defines whether the search should keep on searching until an element with the given locator is found (note that if True and no element was found an ElementNotFound is raised).

**Note:**

> Keep in mind that by default the search strategy is for searching `siblings` of the initial element found (so, by default, after the first element is found a tree traversal is not done and only sibling elements from the initial element are found). Use the `all` search strategy to search for all elements.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L563)

```python
find_many(
    locator: str,
    search_depth: int = 8,
    timeout: Optional[float] = None,
    search_strategy: Literal['siblings', 'all'] = 'siblings',
    wait_for_element=False
) → List[ForwardRef('ControlElement')]
```

______________________________________________________________________

### `get_parent`

**Returns:**
The parent element for this control.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L113)

```python
get_parent() → Optional[ForwardRef('ControlElement')]
```

______________________________________________________________________

### `get_text`

Get text from element (for elements which allow the GetWindowText action).

**Args:**

- <b>`locator`</b>:  Optional locator if it should target a child element.

- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is given.

**Returns:**
The window text of the element.

**Example:**

```python
from robocorp import windows
window = windows.find_window('...')
date = window.get_text('type:Edit name:"Date of birth"')
```

**Raises:**
ActionNotPossible if the text cannot be gotten from this element.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L1286)

```python
get_text(
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None
) → Optional[str]
```

______________________________________________________________________

### `get_value`

Get value from element (usually used with combo boxes or text controls).

**Args:**

- <b>`locator`</b>:  Optional locator if it should target a child element.

- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is given.

**Returns:**
The value of the element.

**Example:**

```python
from robocorp import windows
window = windows.find_window('...')
date = window.get_value('type:Edit name:"Date of birth"')
```

**Raises:**
ActionNotPossible if the text cannot be gotten from this element.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L1344)

```python
get_value(
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None
) → Optional[str]
```

______________________________________________________________________

### `has_keyboard_focus`

**Returns:**
True if this control currently has keyboard focus.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L191)

```python
has_keyboard_focus() → bool
```

______________________________________________________________________

### `has_valid_geometry`

**Returns:**
True if the geometry of this element is valid and False otherwise.

**Note:**

> This value is based on cached coordinates. Call `update_geometry()` to check it based on the current bounds of the control.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L380)

```python
has_valid_geometry() → bool
```

______________________________________________________________________

### `inspect`

Starts inspecting with this element as the root element upon which other elements will be found (i.e.: only elements under this element in the hierarchy will be inspected, other elements can only be inspected if the inspection root is changed).

**Example:**

```python
from robocorp import windows
windows.find_window('Calculator').inspect()
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L94)

```python
inspect() → None
```

______________________________________________________________________

### `is_disposed`

**Returns:**
True if the underlying control is already disposed and False otherwise.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L169)

```python
is_disposed() → bool
```

______________________________________________________________________

### `is_same_as`

**Args:**

- <b>`other`</b>:  The element to compare to.

**Returns:**
True if this elements points to the same element representedby the other control.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L123)

```python
is_same_as(other: 'ControlElement') → bool
```

______________________________________________________________________

### `iter_children`

Iterates over all of the children of this element up to the max_depth provided.

**Args:**

- <b>`max_depth`</b>:  the maximum depth which should be iterated to.

**Returns:**
An iterator of `ControlElement` which provides the descendants ofthis element.

**Note:**

> Iteration over too many items can be slow. Try to keep the max depth up to a minimum to avoid slow iterations.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L652)

```python
iter_children(max_depth: int = 8) → Iterator[ForwardRef('ControlElement')]
```

______________________________________________________________________

### `log_screenshot`

Makes a screenshot of the given element and saves it into the `log.html` using `robocorp-log`. If `robocorp-log` is not available returns False.

**Args:**

- <b>`level`</b>:  The log level for the screenshot.

- <b>`locator`</b>:  Optional locator if it should target a child element.

- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is given.

**Returns:**
True if the screenshot was successfuly saved using `robocorp-log`and False otherwise.

**Example:**

```python
from robocorp import windows
windows.desktop().log_screenshot('ERROR')
```

**Raises:**
ElementNotFound if the locator was passed but it was not possibleto find the element.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L1719)

```python
log_screenshot(
    level='INFO',
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None
) → bool
```

______________________________________________________________________

### `middle_click`

Middle-clicks an element using the mouse.

**Args:**

- <b>`locator`</b>:  If given the child element which matches this locator will be middle-clicked.

- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is passed.

- <b>`wait_time`</b>:  The time to wait after middle-clicking the element. If not passed the default value found in the config is used.

**Example:**

Middle-click using a locator:

```python
from robocorp import windows
windows.find_window('Calculator').middle_click('id:button1')
```

Click customizing wait time after the middle-click:

```python
from robocorp import windows
calculator_window = windows.find_window('Calculator')
calculator_window.find('name:SendButton').middle_click(wait_time=5.0)
```

Make an existing window foreground so that it can be middle-clicked:

```python
window.foreground_window()
window.middle_click('name:SendButton', wait_time=5.0)
```

**Returns:**
The clicked element.

**Note:**

> The element clicked must be visible in the screen, if it's hidden by some other window or control the middle-click will not work.

**Raises:**

- <b>`ActionNotPossible`</b>:  if element does not allow the middle-click action.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L1002)

```python
middle_click(
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None
) → ControlElement
```

______________________________________________________________________

### `mouse_hover`

Moves the mouse to the center of this element to simulate a mouse hovering.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L798)

```python
mouse_hover() → None
```

______________________________________________________________________

### `print_tree`

Print a tree of control elements.

A Windows application structure can contain multilevel element structure. Understanding this structure is crucial for creating locators. (based on controls' details and their parent-child relationship)

This method can be used to output logs of application's element structure.

The printed element attributes correspond to the values that may be used to create a locator to find the actual wanted element.

**Args:**

- <b>`stream`</b>:  The stream to which the text should be printed (if not given, sys.stdout is used).

- <b>`show_properties`</b>:  Whether the properties of each element should be printed (off by default as it can be considerably slower and makes the output very verbose).

- <b>`max_depth`</b>:  Up to which depth the tree should be printed.

**Example:**

Print the top-level window elements:

```python
from robocorp import windows
windows.desktop().print_tree()
```

**Example:**

Print the tree starting at some other element:

```python
from robocorp import windows
windows.find("Calculator > path:2|3").print_tree()
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L680)

```python
print_tree(
    stream=None,
    show_properties: bool = False,
    max_depth: int = 8
) → None
```

______________________________________________________________________

### `right_click`

Right-clicks an element using the mouse.

**Args:**

- <b>`locator`</b>:  If given the child element which matches this locator will be right-clicked.
- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).
- <b>`wait_time`</b>:  The time to wait after right-clicking the element. If not passed the default value found in the config is used.
- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is passed.

**Example:**

Right-click using a locator:

```python
from robocorp import windows
windows.find_window('Calculator').right_click('id:button1')
```

Click customizing wait time after the right-click:

```python
from robocorp import windows
calculator_window = windows.find_window('Calculator')
calculator_window.find('name:SendButton').right_click(wait_time=5.0)
```

Make an existing window foreground so that it can be right-clicked:

```python
window.foreground_window()
window.right_click('name:SendButton', wait_time=5.0)
```

**Returns:**
The clicked element.

**Note:**

> The element clicked must be visible in the screen, if it's hidden by some other window or control the right-click will not work.

**Raises:**

- <b>`ActionNotPossible`</b>:  if element does not allow the right-click action.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L939)

```python
right_click(
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None
) → ControlElement
```

______________________________________________________________________

### `screenshot`

Makes a screenshot of the given element and saves it into the given file.

**Args:**

- <b>`filename`</b>:  The file where the image should be saved.

- <b>`img_format`</b>:  The format in which the image should be saved (by default detects it from the filename).

- <b>`locator`</b>:  Optional locator if it should target a child element.

- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is given.

**Example:**

```python
from robocorp import windows
windows.desktop().screenshot('desktop.png')
windows.find_window('subname:Notepad').screenshot('output/notepad.png')
```

**Returns:**
The absolute path to the image saved or None if it was not possibleto obtain the screenshot.

**Raises:**
ElementNotFound if the locator was passed but it was not possibleto find the element.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L1661)

```python
screenshot(
    filename: Union[str, Path],
    img_format: Optional[str] = None,
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None
) → Optional[str]
```

______________________________________________________________________

### `screenshot_pil`

Makes a screenshot of the given element and returns it as a PIL image.

**Args:**

- <b>`locator`</b>:  Optional locator if it should target a child element.

- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is given.

**Example:**

```python
from robocorp import windows
img = windows.find_window('Notepad').screenshot_pil()
if img is not None:
    ...
```

**Returns:**
The PIL image if it was possible to do the screenshot or None ifit was not possible to do the screenshot.

**Raises:**
ElementNotFound if the locator was passed but it was not possibleto find the element.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L1610)

```python
screenshot_pil(
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None
) → Optional[ForwardRef('Image')]
```

______________________________________________________________________

### `select`

Select a value on the passed element if such action is supported.

**Args:**

- <b>`value`</b>:  value to select on element.

- <b>`locator`</b>:  If given the child element which matches this locator will be used for the selection.

- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is passed.

**Returns:**
The element used in the selection.

**Raises:**
ActionNotPossible if the element does not allow the `Select` action.

**Note:**

> This is usually used with combo box elements.

**Example:**

```python
element.select("22", locator="id:FontSizeComboBox")
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L1124)

```python
select(
    value: str,
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None
) → ControlElement
```

______________________________________________________________________

### `send_keys`

Sends the given keys to the element (simulates typing keys on the keyboard).

**Args:**

- <b>`keys`</b>:  The keys to be sent. Special keys may be sent as {Ctrl}{Alt}{Delete}, etc.

Some examples of valid key combinations are shown below:

```python
 '{Ctrl}a{Delete}{Ctrl}v{Ctrl}s{Ctrl}{Shift}s{Win}e{PageDown}'  # press Ctrl+a, Delete, Ctrl+v, Ctrl+s, Ctrl+Shift+s, Win+e, PageDown
 '{Ctrl}(AB)({Shift}(123))'  # press Ctrl+A+B, type '(', press Shift+1+2+3, type ')', if '()' follows a hold key, hold key won't release util ')'
 '{Ctrl}{a 3}'  # press Ctrl+a at the same time, release Ctrl+a, then type 'a' 2 times
 '{a 3}{B 5}'  # type 'a' 3 times, type 'B' 5 times
 '{{}Hello{}}abc {a}{b}{c} test{} 3}{!}{a} (){(}{)}'  # type: '{Hello}abc abc test}}}!a ()()'
 '0123456789{Enter}'
 'ABCDEFGHIJKLMNOPQRSTUVWXYZ{Enter}'
 'abcdefghijklmnopqrstuvwxyz{Enter}'
 '`~!@#$%^&*()-_=+{Enter}'
 '[]{{}{}}\|;:'",<.>/?{Enter}'
```

- <b>`interval`</b>:  Time between each sent key. (defaults to 0.01 seconds)

- <b>`send_enter`</b>:  If `True` then the {Enter} key is pressed at the end of the sent keys.

- <b>`locator`</b>:  If given the child element which matches this locator will be used to send the keys.

- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is passed.

- <b>`wait_time`</b>:  The time to wait after sending the keys to the element. If not passed the default value found in the config is used.

**Returns:**
The element to which the keys were sent.

**Example:**

```python
from robocorp import windows

windows.desktop().send_keys('{Ctrl}{F4}')
windows.find_window('Calculator').send_keys('96+4=', send_enter=True)
```

**Raises:**

- <b>`ActionNotPossible`</b>:  if the element does not allow the SendKeys action.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L1184)

```python
send_keys(
    keys: Optional[str] = None,
    interval: float = 0.01,
    send_enter: bool = False,
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None
) → ControlElement
```

______________________________________________________________________

### `set_focus`

Sets the view focus to the element (or elemen specified by the locator).

**Args:**

- <b>`locator`</b>:  Optional locator if it should target a child element.

- <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is given.

**Example:**

```python
from robocorp import windows
chrome = windows.find_window('executable:chrome')
bt = chrome.set_focus('name:Buy type:Button')
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L1783)

```python
set_focus(
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None
) → ControlElement
```

______________________________________________________________________

### `set_value`

Set the value in the element (usually used with combo boxes ortext controls).

**Args:**

```
     - <b>`value`</b>:  String value to be set.


     - <b>`append`</b>:  `False` for setting the value, `True` for appending it. (OFF by default)


     - <b>`enter`</b>:  Set it to `True` to press the `Enter` key at the end of the input. (nothing is pressed by default)


     - <b>`newline`</b>:  Set it to `True` to add a new line at the end of the value. (no EOL included by default; this won't work with `send_keys_fallback` enabled)


     - <b>`send_keys_fallback`</b>:  Tries to set the value by sending it through keys if the main way of setting it fails. (enabled by default)


     - <b>`validator`</b>:  Function receiving two parameters post-setting, the expected and the current value, which returns `True` if the two values match. (by default, the method will raise if the values are different, set this to `None` to disable validation or pass your custom function instead)


     - <b>`locator`</b>:  Optional locator if it should target a child element.


     - <b>`search_depth`</b>:  Used as the depth to search for the locator (only used if the `locator` is specified).


     - <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `locator` is given.
```

**Note:**

> It is important to set `append=True` to keep the current text in the element. Other option is to read the current text into a variable, then modify that value as you wish and pass it to `set_value` for a complete text replacement. (without setting the `append` flag).
> Returns: The element object identified through the passed `locator` or this element if no `locator` was passed.

**Raises:**

```
     - <b>`ActionNotPossible`</b>:  if the element does not allow the `SetValue` action to be run on it nor having `send_keys_fallback=True`.
     - <b>`ValueError`</b>:  if the new value to be set can't be set correctly.
```

**Example:**

```python
# Set value to "ab c"
window.set_value('ab c', locator='type:DataItem name:column1')

# Press ENTER after setting the value.
window.set_value('console.txt', locator='type:Edit name:"File name:"', enter=True)

# Add newline (manually) at the end of the string.
element = window.find('name:"Text Editor"')
element.set_value(r'abc


# Add newline with parameter.
element.set_value('abc', newline=True)

# Validation disabled.
element.set_value('2nd line', append=True, newline=True, validator=None)
```

**Example:**

````python
from robocorp import windows
window = windows.find_window('Document - WordPad')
element = window.find('Rich Text Window')
element.set_value(value="My text", send_keys_fallback=True)
text = element.get_value(elem)
print(text)


 [**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L1465)

```python
set_value(
    value: str,
    append: bool = False,
    enter: bool = False,
    newline: bool = False,
    send_keys_fallback: bool = True,
    validator: Optional[Callable] = _SentinelValidator,
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None
) → ControlElement
````

______________________________________________________________________

### `update_geometry`

This method may be called to update the cached coordinates of the control bounds.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_control_element.py#L395)

```python
update_geometry() → None
```

______________________________________________________________________

# Class `Desktop`

The desktop is the control, containing other top-level windows.

The elements provided by robocorp-windows are organized as: Desktop (root control)WindowElement (top-level windows)ControlElement (controls inside a window)

### `__init__`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_desktop.py#L24)

```python
__init__() → None
```

## Properties

- `automation_id`

**Returns:**
The automation id of the underlying control wrapped in this class (matches the locator `automationid` or `id`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `bottom`

**Returns:**
The bottom bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `class_name`

**Returns:**
The class name of the underlying control wrapped in this class (matches the locator `class`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `control_type`

**Returns:**
The control type of the underlying control wrapped in this class (matches the locator `control` or `type`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `handle`

**Returns:**
The internal native window handle from the control wrapped in this class.

- `height`

**Returns:**
The height of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `left`

**Returns:**
The left bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `name`

**Returns:**
The name of the underlying control wrapped in this class (matches the locator `name`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `path`

Provides the relative path in which this element was found

Note: this is relative to the element which was used for the `find` or `find_window` and cannot be used as an absolute path to be used to find the control from the desktop.

- `rectangle`

**Returns:**
A tuple with (left, top, right, bottom) -- (all -1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `right`

**Returns:**
The right bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `top`

**Returns:**
The top bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `ui_automation_control`

Provides the Control actually wrapped by this ControlElement. Can be used as an escape hatch if some functionality is not directly covered by this class (in general this API should only be used if a better API isn't directly available in the ControlElement).

- `width`

**Returns:**
The width of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `xcenter`

**Returns:**
The x position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `ycenter`

**Returns:**
The y position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

## Methods

______________________________________________________________________

### `close_windows`

Closes the windows matching the given locator.

Note that by default the process tree will be force-killed by using the `pid` associated to the window. `use_close_button` can be set to True to try to close it by clicking on the close button (in this case any confirmation dialog must be explicitly handled).

**Args:**

- <b>`locator`</b>:  The locator which should be used to find windows to be closed.

- <b>`search_depth`</b>:  The search depth to be used to find windows (by default equals 1, meaning that only top-level windows will be closed). Note that windows are closed by force-killing the pid related to the window.

- <b>`timeout`</b>:  The search for a window with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards (if `wait_for_window` is True). Only used if `wait_for_window` is True. If not given the global config timeout will be used.

- <b>`wait_for_window`</b>:  If True windows this method will keep searching for windows until a window is found or until the timeout is reached (an ElementNotFound is raised if no window was found until the timeout is reached, otherwise an empty list is returned).

- <b>`wait_time`</b>:  A time to wait after closing each window.

- <b>`use_close_button`</b>:  If True tries to close the window by searching for a button with the locator: 'control:ButtonControl name:Close' and clicking on it (in this case any confirmation dialog must be explicitly handled).

- <b>`close_button_locator`</b>:  Only used if `use_close_button` is True. This is the locator to be used to find the close button.

**Returns:**
The number of closed windows.

**Raises:**

- <b>`ElementNotFound`</b>:  if wait_for_window is True and the timeout was reached.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_desktop.py#L244)

```python
close_windows(
    locator: str,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_for_window: bool = False,
    wait_time: Optional[float] = 0,
    use_close_button: bool = False,
    close_button_locator: str = 'control:ButtonControl name:Close'
) → int
```

______________________________________________________________________

### `drag_and_drop`

Drag and drop the source element into target element.

**Args:**

- <b>`source`</b>:  Source element for the operation.
- <b>`target`</b>:  Target element for the operation
- <b>`speed`</b>:  The speed at which the mouse should move to make the drag (1 means regular speed, values bigger than 1 mean that the mouse should move faster and values lower than 1 mean that the mouse should move slower).
- <b>`hold_ctrl`</b>:  Whether the `Ctrl` key should be hold while doing the drag and drop (on some cases this means that a copy of the item should be done).
- <b>`wait_time`</b>:  Time to wait after drop, defaults to 1.0 second.

**Example:**

```python
# Get the opened explorer on the c:\temp folder
from robocorp import windows
explorer1 = windows.find_window(r'name:C:   emp executable:explorer.exe')
explorer2 = windows.find_window(r'name:C:   emp2 executable:explorer.exe')

# copying a file, report.html, from source (File Explorer) window
# into a target (File Explorer) Window
report_html = explorer1.find('name:report.html type:ListItem')
items_view = explorer2.find('name:"Items View"')
explorer.drag_and_drop(report_html, items_view, hold_ctrl=True)
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_desktop.py#L498)

```python
drag_and_drop(
    source: 'ControlElement',
    target: 'ControlElement',
    speed: float = 1.0,
    hold_ctrl: Optional[bool] = False,
    wait_time: float = 1.0
)
```

______________________________________________________________________

### `find_window`

Finds windows matching the given locator.

**Args:**

- <b>`locator`</b>:  The locator which should be used to find a window.

- <b>`search_depth`</b>:  The search depth to be used to find the window (by default equals 1, meaning that only top-level windows will be found).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used.

- <b>`wait_time`</b>:  The time to wait after the windows was found. If not given the global config wait_time will be used.

- <b>`foreground`</b>:  If True the matched window will be made the foreground window.

- <b>`raise_error`</b>:  Do not raise and return `None` when this is set to `True` and such a window isn't found.

**Raises:**
`ElementNotFound` if a window with the given locator could not be found.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_desktop.py#L155)

```python
find_window(
    locator: str,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None,
    foreground: bool = True,
    raise_error: bool = True
) → Optional[ForwardRef('WindowElement')]
```

______________________________________________________________________

### `find_windows`

Finds windows matching the given locator.

**Args:**

- <b>`locator`</b>:  The locator which should be used to find windows (if not given, all windows are returned).

- <b>`search_depth`</b>:  The search depth to be used to find windows (by default equals 1, meaning that only top-level windows will be found).

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used. Only used if `wait_for_window` is True.

- <b>`wait_for_window`</b>:  Defines whether the search should keep on searching until a window with the given locator is found (note that if True and no window was found a ElementNotFound is raised).

**Returns:**
The `WindowElement`s which should be used to interact with the window.

**Example:**

```python
window = find_windows('Calculator')
window = find_windows('name:Calculator')
window = find_windows('subname:Notepad')
window = find_windows('regex:.*Notepad')
window = find_windows('executable:Spotify.exe')
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_desktop.py#L196)

```python
find_windows(
    locator: str,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_for_window: bool = False
) → List[ForwardRef('WindowElement')]
```

______________________________________________________________________

### `get_win_version`

Windows only utility which returns the current Windows major version.

**Returns:**
The current Windows major version (i.e.: '10', '11').

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_desktop.py#L358)

```python
get_win_version() → str
```

______________________________________________________________________

### `iter_children`

Iterates over all of the children of this element up to the max_depth provided.

**Args:**

- <b>`max_depth`</b>:  the maximum depth which should be iterated to.

**Returns:**
An iterator of `ControlElement` which provides the descendants ofthis element.

**Note:**

> Iteration over too many items can be slow. Try to keep the max depth up to a minimum to avoid slow iterations.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_desktop.py#L101)

```python
iter_children(max_depth: int = 1) → Iterator[ForwardRef('ControlElement')]
```

______________________________________________________________________

### `print_tree`

Print a tree of control elements.

A Windows application structure can contain multilevel element structure. Understanding this structure is crucial for creating locators. (based on controls' details and their parent-child relationship)

This keyword can be used to output logs of application's element structure.

The printed element attributes correspond to the values that may be used to create a locator to find the actual wanted element.

**Args:**

- <b>`stream`</b>:  The stream to which the text should be printed (if not given, sys.stdout is used).

- <b>`show_properties`</b>:  Whether the properties of each element should be printed (off by default as it can be considerably slower and makes the output very verbose).

- <b>`max_depth`</b>:  Up to which depth the tree should be printed.

**Example:**

Print the top-level window elements:

```python
from robocorp import windows
windows.desktop().print_tree()
```

**Example:**

Print the tree starting at some other element:

```python
from robocorp import windows
windows.find_window("Calculator").find("path:2|3").print_tree()
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_desktop.py#L44)

```python
print_tree(
    stream=None,
    show_properties: bool = False,
    max_depth: int = 1
) → None
```

______________________________________________________________________

### `wait_for_active_window`

Waits for a window with the given locator to be made active.

**Args:**

- <b>`locator`</b>:  The locator that the active window must match.
- <b>`timeout`</b>:  Timeout (in **seconds**) to wait for a window with the given locator to be made active.
- <b>`wait_time`</b>:  A time to wait after the active window is found.

**Raises:**
ElementNotFound if no window was found as active until the timeoutwas reached.

Note: if there's a matching window which matches the locator but it's not the active one, this will fail (consider using `find_window`for this use case).

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_desktop.py#L382)

```python
wait_for_active_window(
    locator: str,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None
) → WindowElement
```

______________________________________________________________________

### `windows_run`

Use Windows `Run window` to launch an application.

Activated by pressing `Win + R`. Then the app name is typed in and finally the "Enter" key is pressed.

**Args:**

- <b>`text`</b>:  Text to enter into the Run input field. (e.g. `Notepad`)
- <b>`wait_time`</b>:  Time to sleep after the searched app is executed. (1s by default)

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_desktop.py#L320)

```python
windows_run(text: str, wait_time: float = 1) → None
```

______________________________________________________________________

### `windows_search`

Use Windows `search window` to launch application.

Activated by pressing `win + s`.

**Args:**

- <b>`text`</b>:  Text to enter into search input field (e.g. `Notepad`)
- <b>`wait_time`</b>:  sleep time after search has been entered (default 3.0 seconds)

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_desktop.py#L340)

```python
windows_search(text: str, wait_time: float = 3.0) → None
```

______________________________________________________________________

# Class `str`

str(object='') -> str str(bytes_or_buffer\[, encoding\[, errors\]\]) -> str

Create a new string object from the given object. If encoding or errors is specified, then the object must expose a data buffer that will be decoded using the given encoding and error handler. Otherwise, returns the result of object.__str__() (if defined) or repr(object). encoding defaults to sys.getdefaultencoding(). errors defaults to 'strict'.

______________________________________________________________________

# Class `WindowElement`

Class used to interact with a window.

### `__init__`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_window_element.py#L34)

```python
__init__(wrapped: '_UIAutomationControlWrapper')
```

## Properties

- `automation_id`

**Returns:**
The automation id of the underlying control wrapped in this class (matches the locator `automationid` or `id`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `bottom`

**Returns:**
The bottom bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `class_name`

**Returns:**
The class name of the underlying control wrapped in this class (matches the locator `class`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `control_type`

**Returns:**
The control type of the underlying control wrapped in this class (matches the locator `control` or `type`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `executable`

**Returns:**
The executable associated to this window (or None if it was not possible to get it).

- `handle`

**Returns:**
The internal native window handle from the control wrapped in this class.

- `height`

**Returns:**
The height of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `left`

**Returns:**
The left bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `name`

**Returns:**
The name of the underlying control wrapped in this class (matches the locator `name`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

- `path`

Provides the relative path in which this element was found

Note: this is relative to the element which was used for the `find` or `find_window` and cannot be used as an absolute path to be used to find the control from the desktop.

- `pid`

Provides the pid of the process related to the Window.

**Raises:**
COMError if the window was already disposed.

- `rectangle`

**Returns:**
A tuple with (left, top, right, bottom) -- (all -1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `right`

**Returns:**
The right bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `top`

**Returns:**
The top bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `ui_automation_control`

Provides the Control actually wrapped by this ControlElement. Can be used as an escape hatch if some functionality is not directly covered by this class (in general this API should only be used if a better API isn't directly available in the ControlElement).

- `width`

**Returns:**
The width of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `xcenter`

**Returns:**
The x position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

- `ycenter`

**Returns:**
The y position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

## Methods

______________________________________________________________________

### `close_window`

Closes the windows matching the given locator.

Note that by default the process tree will be force-killed by using the `pid` associated to this window. `use_close_button` can be set to True to try to close it by clicking on the close button (in this case any confirmation dialog must be explicitly handled).

**Args:**

- <b>`use_close_button`</b>:  If True tries to close the window by searching for a button with the locator: 'control:ButtonControl name:Close' and clicking on it (in this case any confirmation dialog must be explicitly handled).

- <b>`close_button_locator`</b>:  Only used if `use_close_button` is True. This is the locator to be used to find the close button.

**Returns:**
True if the window was closed by this function and False otherwise.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_window_element.py#L350)

```python
close_window(
    use_close_button: bool = False,
    close_button_locator: str = 'control:ButtonControl name:Close'
) → bool
```

______________________________________________________________________

### `find_child_window`

Find a child window of this window given its locator.

**Args:**

- <b>`locator`</b>:  The locator which should be used to find a child window.

- <b>`search_depth`</b>:  The search depth to be used to find the window.

- <b>`timeout`</b>:  The search for a child with the given locator will be retried until the given timeout (in **seconds**) elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards. If not given the global config timeout will be used.

- <b>`wait_time`</b>:  The time to wait after the window was found. If not given the global config wait_time will be used.

- <b>`foreground`</b>:  If True the matched window will be made the foreground window.

- <b>`raise_error`</b>:  Do not raise and return `None` when this is set to `True` and such a window isn't found.

**Raises:**
`ElementNotFound` if a window with the given locator could not befound.

**Example:**

```python
from robocorp import windows
sage = windows.find_window('subname:"Sage 50" type:Window')

# actions on the main application window
# ...
# get control of child window of Sage application
child_window = sage.find_child_window('subname:"Test Company" depth:1')
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_window_element.py#L160)

```python
find_child_window(
    locator: str,
    search_depth: int = 8,
    foreground: bool = True,
    wait_time: Optional[float] = None,
    timeout: Optional[float] = None,
    raise_error: bool = True
) → Optional[ForwardRef('WindowElement')]
```

______________________________________________________________________

### `foreground_window`

Bring this window to the foreground (note: `find_window` makes the window the foreground window by default).

**Example:**

```python
from robocorp import windows
calculator = windows.find_window('Calculator', foreground=False)
...
calculator.foreground_window()
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_window_element.py#L219)

```python
foreground_window() → WindowElement
```

______________________________________________________________________

### `is_active`

**Returns:**
True if this is currently the active window and False otherwise.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_window_element.py#L96)

```python
is_active() → bool
```

______________________________________________________________________

### `is_running`

**Returns:**
True if the pid associated to this window is still running and False otherwise.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_window_element.py#L330)

```python
is_running() → bool
```

______________________________________________________________________

### `maximize_window`

Maximizes the window.

**Returns:**
True if it was possible to maximize the window and False otherwise.

**Example:**

```python
from robocorp import windows
windows.find_window('executable:Spotify.exe').maximize_window()
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_window_element.py#L270)

```python
maximize_window() → bool
```

______________________________________________________________________

### `minimize_window`

Maximizes the window.

**Returns:**
True if it was possible to minimize the window and False otherwise.

**Example:**

```python
from robocorp import windows
windows.find_window('executable:Spotify.exe').minimize_window()
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_window_element.py#L254)

```python
minimize_window() → bool
```

______________________________________________________________________

### `restore_window`

Restores the window.

**Returns:**
True if it was possible to restore the window and False otherwise.

**Example:**

```python
from robocorp import windows
windows.find_window('executable:Spotify.exe').restore_window()
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_window_element.py#L286)

```python
restore_window() → bool
```

______________________________________________________________________

### `set_window_pos`

Sets the window position.

**Args:**

- <b>`x`</b>:  The x-coordinate of the window.
- <b>`y`</b>:  The y-coordinate of the window.
- <b>`width`</b>:  The width of the window.
- <b>`height`</b>:  The height of the window.

**Example:**

```python
from robocorp import windows
desktop = windows.desktop()
explorer = windows.find_window('executable:explorer.exe')
# Set the size of the window to be half of the screen.
explorer.set_window_pos(0, 0, desktop.width / 2, desktop.height)
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_window_element.py#L302)

```python
set_window_pos(x: int, y: int, width: int, height: int) → WindowElement
```

# Exceptions

______________________________________________________________________

## `ActionNotPossible`

Action is not possible for the given Control.

______________________________________________________________________

## `ElementDisposed`

The existing element was disposed and is no longer available.

______________________________________________________________________

## `ElementNotFound`

No matching elements were found.

______________________________________________________________________

## `InvalidLocatorError`

The locator specified is invalid.

______________________________________________________________________

## `InvalidStrategyDuplicated`

A given strategy is defined more than once in the same level.

______________________________________________________________________

## `ParseError`

The locator specified is invalid because it was not possible to parse it properly.

### `__init__`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/windows/src/robocorp/windows/_errors.py#L26)

```python
__init__(msg, index)
```
