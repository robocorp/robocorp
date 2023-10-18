<!-- markdownlint-disable -->

# module `robocorp.windows`

**Source:** [`__init__.py:0`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/__init__.py#L0)

The `robocorp-windows` library is a library to be used to interact with native widgets on the Windows OS.

______________________________________________________________________

## function `get_icon_from_file`

**Source:** [`__init__.py:32`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/__init__.py#L32)

```python
get_icon_from_file(path: str) → Optional[ForwardRef('Image')]
```

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

______________________________________________________________________

## function `desktop`

**Source:** [`__init__.py:80`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/__init__.py#L80)

```python
desktop() → Desktop
```

Provides the desktop element (which is the root control containing top-level windows).

The elements provided by robocorp-windows are organized as: Desktop (root control)WindowElement (top-level windows)ControlElement (controls inside a window)

**Returns:**
The Desktop element.

______________________________________________________________________

## function `config`

**Source:** [`__init__.py:96`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/__init__.py#L96)

```python
config() → Config
```

Provides an instance to configure the basic settings such as the default timeout, whether to simulate mouse movements, showing verbose errors on failures, screenshot on error (when running with robocorp-tasks), etc.

**Returns:**
Config object to be used to configure the settings.

**Example:**

```
from robocorp import windows
config = windows.config()
config.verbose_errors = True
```

______________________________________________________________________

## function `find_window`

**Source:** [`__init__.py:117`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/__init__.py#L117)

```python
find_window(
    locator: str,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None,
    foreground: bool = True
) → WindowElement
```

Finds the first window matching the passed locator.

**Args:**

- <b>`locator`</b>:  This is the locator which should be used to find the window.

- <b>`search_depth`</b>:  The search depth to find the window (by default == 1, meaning that only top-level windows will be found).

timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

- <b>`wait_time`</b>:  The time to wait after finding the window. If not passed the default value found in the config is used.

- <b>`foreground`</b>:  Whether the found window should be made top-level when found.

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

______________________________________________________________________

## function `find_windows`

**Source:** [`__init__.py:163`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/__init__.py#L163)

```python
find_windows(
    locator: str = 'regex:.*',
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_for_window: bool = False
) → List[ForwardRef('WindowElement')]
```

Finds all windows matching the given locator.

**Args:**

- <b>`locator`</b>:  The locator which should be used to find windows (if not given, all windows are returned).

- <b>`search_depth`</b>:  The search depth to be used to find windows (by default equals 1, meaning that only top-level windows will be found).

timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

Only used if `wait_for_window` is True.

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

______________________________________________________________________

## function `wait_for_condition`

**Source:** [`__init__.py:211`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/__init__.py#L211)

```python
wait_for_condition(
    condition: Callable[[], bool],
    timeout: float = 8.0,
    msg: Optional[Callable[[], str]] = None
)
```

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

______________________________________________________________________

## class `Desktop`

**Source:** [`_desktop.py:14`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L14)

The desktop is the control, containing other top-level windows.

The elements provided by robocorp-windows are organized as: Desktop (root control)WindowElement (top-level windows)ControlElement (controls inside a window)

### method `__init__`

**Source:** [`_desktop.py:24`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L24)

```python
__init__() → None
```

#### property `automation_id`

**Returns:**
The automation id of the underlying control wrapped in this class (matches the locator `automationid` or `id`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `bottom`

**Returns:**
The bottom bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `class_name`

**Returns:**
The class name of the underlying control wrapped in this class (matches the locator `class`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `control_type`

**Returns:**
The control type of the underlying control wrapped in this class (matches the locator `control` or `type`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `handle`

**Returns:**
The internal native window handle from the control wrapped in this class.

#### property `height`

**Returns:**
The height of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `left`

**Returns:**
The left bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `name`

**Returns:**
The name of the underlying control wrapped in this class (matches the locator `name`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `path`

Provides the relative path in which this element was found

Note: this is relative to the element which was used for the `find` or `find_window` and cannot be used as an absolute path to be used to find the control from the desktop.

#### property `rectangle`

**Returns:**
A tuple with (left, top, right, bottom) -- (all -1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `right`

**Returns:**
The right bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `top`

**Returns:**
The top bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `ui_automation_control`

Provides the Control actually wrapped by this ControlElement. Can be used as an escape hatch if some functionality is not directly covered by this class (in general this API should only be used if a better API isn't directly available in the ControlElement).

#### property `width`

**Returns:**
The width of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `xcenter`

**Returns:**
The x position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `ycenter`

**Returns:**
The y position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

______________________________________________________________________

### method `close_windows`

**Source:** [`_desktop.py:215`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L215)

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

Closes the windows matching the given locator.

Note that by default the process tree will be force-killed by using the `pid` associated to the window. `use_close_button` can be set to True to try to close it by clicking on the close button (in this case any confirmation dialog must be explicitly handled).

**Args:**

- <b>`locator`</b>:  The locator which should be used to find windows to be closed.

- <b>`search_depth`</b>:  The search depth to be used to find windows (by default equals 1, meaning that only top-level windows will be closed). Note that windows are closed by force-killing the pid related to the window.

timeout: The search for a window with the given locator will be retried until the given timeout elapses. At least one full search up to the given depth will always be done and the timeout will only take place afterwards (if `wait_for_window` is True).

Only used if `wait_for_window` is True.

If not given the global config timeout will be used.

- <b>`wait_for_window`</b>:  If True windows this method will keep searching for windows until a window is found or until the timeout is reached (an ElementNotFound is raised if no window was found until the timeout is reached, otherwise an empty list is returned).

- <b>`wait_time`</b>:  A time to wait after closing each window.

- <b>`use_close_button`</b>:  If True tries to close the window by searching

- <b>`for a button with the locator`</b>:  'control:ButtonControl name:Close'and clicking on it (in this case any confirmation dialog must beexplicitly handled).

- <b>`close_button_locator`</b>:  Only used if `use_close_button` is True. This is the locator to be used to find the close button.

**Returns:**
The number of closed windows.

**Raises:**

- <b>`ElementNotFound`</b>:  if wait_for_window is True and the timeout was reached.

______________________________________________________________________

### method `drag_and_drop`

**Source:** [`_desktop.py:467`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L467)

```python
drag_and_drop(
    source: 'ControlElement',
    target: 'ControlElement',
    speed: float = 1.0,
    hold_ctrl: Optional[bool] = False,
    wait_time: float = 1.0
)
```

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

______________________________________________________________________

### method `find_window`

**Source:** [`_desktop.py:119`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L119)

```python
find_window(
    locator: str,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None,
    foreground: bool = True
) → WindowElement
```

Finds windows matching the given locator.

**Args:**

- <b>`locator`</b>:  The locator which should be used to find a window.

- <b>`search_depth`</b>:  The search depth to be used to find the window (by default equals 1, meaning that only top-level windows will be found).

timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

wait_time: The time to wait after the windows was found.

If not given the global config wait_time will be used.

foreground: If True the matched window will be made the foreground window.

**Raises:**
ElementNotFound if a window with the given locator could not befound.

______________________________________________________________________

### method `find_windows`

**Source:** [`_desktop.py:163`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L163)

```python
find_windows(
    locator: str,
    search_depth: int = 1,
    timeout: Optional[float] = None,
    wait_for_window: bool = False
) → List[ForwardRef('WindowElement')]
```

Finds windows matching the given locator.

**Args:**

- <b>`locator`</b>:  The locator which should be used to find windows (if not given, all windows are returned).

- <b>`search_depth`</b>:  The search depth to be used to find windows (by default equals 1, meaning that only top-level windows will be found).

timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

Only used if `wait_for_window` is True.

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

______________________________________________________________________

### method `get_win_version`

**Source:** [`_desktop.py:331`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L331)

```python
get_win_version() → str
```

Windows only utility which returns the current Windows major version.

**Returns:**

- <b>`The current Windows major version (i.e.`</b>:  '10', '11').

______________________________________________________________________

### method `iter_children`

**Source:** [`_desktop.py:101`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L101)

```python
iter_children(max_depth: int = 1) → Iterator[ForwardRef('ControlElement')]
```

Iterates over all of the children of this element up to the max_depth provided.

**Args:**

- <b>`max_depth`</b>:  the maximum depth which should be iterated to.

**Returns:**
An iterator of `ControlElement` which provides the descendants ofthis element.

**Note:**

> Iteration over too many items can be slow. Try to keep the max depth up to a minimum to avoid slow iterations.

______________________________________________________________________

### method `print_tree`

**Source:** [`_desktop.py:44`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L44)

```python
print_tree(
    stream=None,
    show_properties: bool = False,
    max_depth: int = 1
) → None
```

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

______________________________________________________________________

### method `wait_for_active_window`

**Source:** [`_desktop.py:349`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L349)

```python
wait_for_active_window(
    locator: str,
    timeout: Optional[float] = None,
    wait_time: Optional[float] = None
) → WindowElement
```

Waits for a window with the given locator to be made active.

**Args:**

- <b>`locator`</b>:  The locator that the active window must match.
- <b>`timeout`</b>:  Timeout to wait for a window with the given locator to be made active.
- <b>`wait_time`</b>:  A time to wait after the active window is found.

**Raises:**
ElementNotFound if no window was found as active until the timeoutwas reached.

Note: if there's a matching window which matches the locator but it's not the active one, this will fail (consider using `find_window`for this use case).

______________________________________________________________________

### method `windows_run`

**Source:** [`_desktop.py:293`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L293)

```python
windows_run(text: str, wait_time: float = 1) → None
```

Use Windows `Run window` to launch an application.

Activated by pressing `Win + R`. Then the app name is typed in and finally the "Enter" key is pressed.

**Args:**

- <b>`text`</b>:  Text to enter into the Run input field. (e.g. `Notepad`)
- <b>`wait_time`</b>:  Time to sleep after the searched app is executed. (1s by default)

______________________________________________________________________

### method `windows_search`

**Source:** [`_desktop.py:313`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_desktop.py#L313)

```python
windows_search(text: str, wait_time: float = 3.0) → None
```

Use Windows `search window` to launch application.

Activated by pressing `win + s`.

**Args:**

- <b>`text`</b>:  Text to enter into search input field (e.g. `Notepad`)
- <b>`wait_time`</b>:  sleep time after search has been entered (default 3.0 seconds)

______________________________________________________________________

## exception `ActionNotPossible`

**Source:** [`_errors.py:1`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_errors.py#L1)

Action is not possible for the given Control.

______________________________________________________________________

## exception `ElementDisposed`

**Source:** [`_errors.py:9`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_errors.py#L9)

The existing element was disposed and is no longer available.

______________________________________________________________________

## exception `ElementNotFound`

**Source:** [`_errors.py:5`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_errors.py#L5)

No matching elements were found.

______________________________________________________________________

## exception `InvalidLocatorError`

**Source:** [`_errors.py:13`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_errors.py#L13)

The locator specified is invalid.

______________________________________________________________________

## exception `InvalidStrategyDuplicated`

**Source:** [`_errors.py:17`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_errors.py#L17)

A given strategy is defined more than once in the same level.

______________________________________________________________________

## exception `ParseError`

**Source:** [`_errors.py:21`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_errors.py#L21)

The locator specified is invalid because it was not possible to parse it properly.

### method `__init__`

**Source:** [`_errors.py:26`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_errors.py#L26)

```python
__init__(msg, index)
```

______________________________________________________________________

## class `str`

str(object='') -> str str(bytes_or_buffer\[, encoding\[, errors\]\]) -> str

Create a new string object from the given object. If encoding or errors is specified, then the object must expose a data buffer that will be decoded using the given encoding and error handler. Otherwise, returns the result of object.__str__() (if defined) or repr(object). encoding defaults to sys.getdefaultencoding(). errors defaults to 'strict'.

______________________________________________________________________

## class `WindowElement`

**Source:** [`_window_element.py:29`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_window_element.py#L29)

Class used to interact with a window.

### method `__init__`

**Source:** [`_window_element.py:34`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_window_element.py#L34)

```python
__init__(wrapped: '_UIAutomationControlWrapper')
```

#### property `automation_id`

**Returns:**
The automation id of the underlying control wrapped in this class (matches the locator `automationid` or `id`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `bottom`

**Returns:**
The bottom bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `class_name`

**Returns:**
The class name of the underlying control wrapped in this class (matches the locator `class`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `control_type`

**Returns:**
The control type of the underlying control wrapped in this class (matches the locator `control` or `type`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `executable`

**Returns:**
The executable associated to this window (or None if it was not possible to get it).

#### property `handle`

**Returns:**
The internal native window handle from the control wrapped in this class.

#### property `height`

**Returns:**
The height of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `left`

**Returns:**
The left bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `name`

**Returns:**
The name of the underlying control wrapped in this class (matches the locator `name`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `path`

Provides the relative path in which this element was found

Note: this is relative to the element which was used for the `find` or `find_window` and cannot be used as an absolute path to be used to find the control from the desktop.

#### property `pid`

Provides the pid of the process related to the Window.

**Raises:**
COMError if the window was already disposed.

#### property `rectangle`

**Returns:**
A tuple with (left, top, right, bottom) -- (all -1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `right`

**Returns:**
The right bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `top`

**Returns:**
The top bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `ui_automation_control`

Provides the Control actually wrapped by this ControlElement. Can be used as an escape hatch if some functionality is not directly covered by this class (in general this API should only be used if a better API isn't directly available in the ControlElement).

#### property `width`

**Returns:**
The width of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `xcenter`

**Returns:**
The x position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `ycenter`

**Returns:**
The y position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

______________________________________________________________________

### method `close_window`

**Source:** [`_window_element.py:318`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_window_element.py#L318)

```python
close_window(
    use_close_button: bool = False,
    close_button_locator: str = 'control:ButtonControl name:Close'
) → bool
```

Closes the windows matching the given locator.

Note that by default the process tree will be force-killed by using the `pid` associated to this window. `use_close_button` can be set to True to try to close it by clicking on the close button (in this case any confirmation dialog must be explicitly handled).

**Args:**

- <b>`use_close_button`</b>:  If True tries to close the window by searching

- <b>`for a button with the locator`</b>:  'control:ButtonControl name:Close'and clicking on it (in this case any confirmation dialog must beexplicitly handled).

- <b>`close_button_locator`</b>:  Only used if `use_close_button` is True. This is the locator to be used to find the close button.

**Returns:**
True if the window was closed by this function and False otherwise.

______________________________________________________________________

### method `find_child_window`

**Source:** [`_window_element.py:124`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_window_element.py#L124)

```python
find_child_window(
    locator: str,
    search_depth: int = 8,
    foreground: bool = True,
    wait_time: Optional[float] = None,
    timeout: Optional[float] = None
) → WindowElement
```

Find a child window of this window given its locator.

**Args:**

- <b>`locator`</b>:  The locator which should be used to find a child window.

- <b>`search_depth`</b>:  The search depth to be used to find the window.

timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

wait_time: The time to wait after the windows was found.

If not given the global config wait_time will be used.

foreground: If True the matched window will be made the foreground window.

**Raises:**
ElementNotFound if a window with the given locator could not befound.

**Example:**

```python
from robocorp import windows
sage = windows.find_window('subname:"Sage 50" type:Window')

# actions on the main application window
# ...
# get control of child window of Sage application
child_window = sage.find_child_window('subname:"Test Company" depth:1')
```

______________________________________________________________________

### method `foreground_window`

**Source:** [`_window_element.py:184`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_window_element.py#L184)

```python
foreground_window() → WindowElement
```

Bring this window to the foreground (note: `find_window` makes the window the foreground window by default).

**Example:**

```python
from robocorp import windows
calculator = windows.find_window('Calculator', foreground=False)
...
calculator.foreground_window()
```

______________________________________________________________________

### method `is_active`

**Source:** [`_window_element.py:96`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_window_element.py#L96)

```python
is_active() → bool
```

**Returns:**
True if this is currently the active window and False otherwise.

______________________________________________________________________

### method `is_running`

**Source:** [`_window_element.py:298`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_window_element.py#L298)

```python
is_running() → bool
```

**Returns:**
True if the pid associated to this window is still running and False otherwise.

______________________________________________________________________

### method `maximize_window`

**Source:** [`_window_element.py:235`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_window_element.py#L235)

```python
maximize_window() → bool
```

Maximizes the window.

**Returns:**
True if it was possible to maximize the window and False otherwise.

**Example:**

```python
from robocorp import windows
windows.find_window('executable:Spotify.exe').maximize_window()
```

______________________________________________________________________

### method `minimize_window`

**Source:** [`_window_element.py:219`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_window_element.py#L219)

```python
minimize_window() → bool
```

Maximizes the window.

**Returns:**
True if it was possible to minimize the window and False otherwise.

**Example:**

```python
from robocorp import windows
windows.find_window('executable:Spotify.exe').minimize_window()
```

______________________________________________________________________

### method `restore_window`

**Source:** [`_window_element.py:251`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_window_element.py#L251)

```python
restore_window() → bool
```

Restores the window.

**Returns:**
True if it was possible to restore the window and False otherwise.

**Example:**

```python
from robocorp import windows
windows.find_window('executable:Spotify.exe').restore_window()
```

______________________________________________________________________

### method `set_window_pos`

**Source:** [`_window_element.py:267`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_window_element.py#L267)

```python
set_window_pos(x: int, y: int, width: int, height: int) → WindowElement
```

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

______________________________________________________________________

## class `ControlElement`

**Source:** [`_control_element.py:58`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L58)

Class used to interact with a control.

### method `__init__`

**Source:** [`_control_element.py:65`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L65)

```python
__init__(wrapped: '_UIAutomationControlWrapper')
```

#### property `automation_id`

**Returns:**
The automation id of the underlying control wrapped in this class (matches the locator `automationid` or `id`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `bottom`

**Returns:**
The bottom bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `class_name`

**Returns:**
The class name of the underlying control wrapped in this class (matches the locator `class`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `control_type`

**Returns:**
The control type of the underlying control wrapped in this class (matches the locator `control` or `type`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `handle`

**Returns:**
The internal native window handle from the control wrapped in this class.

#### property `height`

**Returns:**
The height of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `left`

**Returns:**
The left bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `name`

**Returns:**
The name of the underlying control wrapped in this class (matches the locator `name`).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned.

#### property `path`

Provides the relative path in which this element was found

Note: this is relative to the element which was used for the `find` or `find_window` and cannot be used as an absolute path to be used to find the control from the desktop.

#### property `rectangle`

**Returns:**
A tuple with (left, top, right, bottom) -- (all -1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `right`

**Returns:**
The right bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `top`

**Returns:**
The top bound of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `ui_automation_control`

Provides the Control actually wrapped by this ControlElement. Can be used as an escape hatch if some functionality is not directly covered by this class (in general this API should only be used if a better API isn't directly available in the ControlElement).

#### property `width`

**Returns:**
The width of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `xcenter`

**Returns:**
The x position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

#### property `ycenter`

**Returns:**
The y position of the center of the control (-1 if invalid).

**Note:**

> This value is cached when the element is created and even if the related value of the underlying control changes the initial value found will still be returned. The method `update_geometry()` may be used to get the new bounds of the control.

______________________________________________________________________

### method `click`

**Source:** [`_control_element.py:741`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L741)

```python
click(
    locator: Optional[str] = None,
    wait_time: Optional[float] = None,
    timeout: Optional[float] = None
) → ControlElement
```

Clicks an element using the mouse.

**Args:**

- <b>`locator`</b>:  If given the child element which matches this locator will be clicked.
- <b>`wait_time`</b>:  The time to wait after clicking the element. If not passed the default value found in the config is used.timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

Only used if `locator` is passed.

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

______________________________________________________________________

### method `double_click`

**Source:** [`_control_element.py:802`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L802)

```python
double_click(
    locator: Optional[str] = None,
    wait_time: Optional[float] = None,
    timeout: Optional[float] = None
) → ControlElement
```

Double-clicks an element using the mouse.

**Args:**

- <b>`locator`</b>:  If given the child element which matches this locator will be double-clicked.
- <b>`wait_time`</b>:  The time to wait after double-clicking the element. If not passed the default value found in the config is used.timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

Only used if `locator` is passed.

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

______________________________________________________________________

### method `find`

**Source:** [`_control_element.py:434`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L434)

```python
find(
    locator: str,
    search_depth: int = 8,
    timeout: Optional[float] = None
) → ControlElement
```

This method may be used to find a control in the descendants of this control.

The first matching element is returned.

**Args:**

- <b>`locator`</b>:  The locator to be used to search a child control.

- <b>`search_depth`</b>:  Up to which depth the hierarchy should be searched.

timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

**Raises:**
ElementNotFound if an element with the given locator could not befound.

______________________________________________________________________

### method `find_many`

**Source:** [`_control_element.py:493`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L493)

```python
find_many(
    locator: str,
    search_depth: int = 8,
    timeout: Optional[float] = None,
    search_strategy: Literal['siblings', 'all'] = 'siblings',
    wait_for_element=False
) → List[ForwardRef('ControlElement')]
```

This method may be used to find multiple descendants of the current element matching the given locator.

**Args:**

- <b>`locator`</b>:  The locator that should be used to find elements.

- <b>`search_depth`</b>:  Up to which depth the tree will be traversed.

timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

Only used if `wait_for_element` is True.

search_strategy: The search strategy to be used to find elements.

`siblings` means that after the first element is found, the tree traversal should be stopped and only sibling elements will be searched.

`all` means that all the elements up to the given search depth will be searched.

- <b>`wait_for_element`</b>:  Defines whether the search should keep on searching until an element with the given locator is found (note that if True and no element was found an ElementNotFound is raised).

**Note:**

> Keep in mind that by default the search strategy is for searching `siblings` of the initial element found (so, by default, after the first element is found a tree traversal is not done and only sibling elements from the initial element are found). Use the `all` search strategy to search for all elements.

______________________________________________________________________

### method `get_parent`

**Source:** [`_control_element.py:99`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L99)

```python
get_parent() → Optional[ForwardRef('ControlElement')]
```

**Returns:**
The parent element for this control.

______________________________________________________________________

### method `get_text`

**Source:** [`_control_element.py:1199`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L1199)

```python
get_text(
    locator: Optional[str] = None,
    timeout: Optional[float] = None
) → Optional[str]
```

Get text from element (for elements which allow the GetWindowText action).

**Args:**

- <b>`locator`</b>:  Optional locator if it should target a child element.

timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

Only used if `locator` is given.

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

______________________________________________________________________

### method `get_value`

**Source:** [`_control_element.py:1256`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L1256)

```python
get_value(
    locator: Optional[str] = None,
    timeout: Optional[float] = None
) → Optional[str]
```

Get value from element.

**Args:**

- <b>`locator`</b>:  Optional locator if it should target a child element.

timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

Only used if `locator` is given.

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

______________________________________________________________________

### method `get_value_pattern`

**Source:** [`_control_element.py:1247`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L1247)

```python
get_value_pattern(
    item: 'Control'
) → Optional[Callable[[], Union[ForwardRef('ValuePattern'), ForwardRef('LegacyIAccessiblePattern')]]]
```

______________________________________________________________________

### method `has_keyboard_focus`

**Source:** [`_control_element.py:177`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L177)

```python
has_keyboard_focus() → bool
```

**Returns:**
True if this control currently has keyboard focus.

______________________________________________________________________

### method `has_valid_geometry`

**Source:** [`_control_element.py:366`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L366)

```python
has_valid_geometry() → bool
```

**Returns:**
True if the geometry of this element is valid and False otherwise.

**Note:**

> This value is based on cached coordinates. Call `update_geometry()` to check it based on the current bounds of the control.

______________________________________________________________________

### method `inspect`

**Source:** [`_control_element.py:80`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L80)

```python
inspect() → None
```

Starts inspecting with this element as the root element upon which other elements will be found (i.e.: only elements under this element in the hierarchy will be inspected, other elements can only be inspected if the inspection root is changed).

**Example:**

```python
from robocorp import windows
windows.find_window('Calculator').inspect()
```

______________________________________________________________________

### method `is_disposed`

**Source:** [`_control_element.py:155`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L155)

```python
is_disposed() → bool
```

**Returns:**
True if the underlying control is already disposed and False otherwise.

______________________________________________________________________

### method `is_same_as`

**Source:** [`_control_element.py:109`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L109)

```python
is_same_as(other: 'ControlElement') → bool
```

**Args:**

- <b>`other`</b>:  The element to compare to.

**Returns:**
True if this elements points to the same element representedby the other control.

______________________________________________________________________

### method `iter_children`

**Source:** [`_control_element.py:592`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L592)

```python
iter_children(max_depth: int = 8) → Iterator[ForwardRef('ControlElement')]
```

Iterates over all of the children of this element up to the max_depth provided.

**Args:**

- <b>`max_depth`</b>:  the maximum depth which should be iterated to.

**Returns:**
An iterator of `ControlElement` which provides the descendants ofthis element.

**Note:**

> Iteration over too many items can be slow. Try to keep the max depth up to a minimum to avoid slow iterations.

______________________________________________________________________

### method `log_screenshot`

**Source:** [`_control_element.py:1578`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L1578)

```python
log_screenshot(
    locator: Optional[str] = None,
    search_depth: int = 8,
    level='INFO',
    timeout: Optional[float] = None
)
```

______________________________________________________________________

### method `middle_click`

**Source:** [`_control_element.py:925`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L925)

```python
middle_click(
    locator: Optional[str] = None,
    wait_time: Optional[float] = None,
    timeout: Optional[float] = None
) → ControlElement
```

Middle-clicks an element using the mouse.

**Args:**

- <b>`locator`</b>:  If given the child element which matches this locator will be middle-clicked.
- <b>`wait_time`</b>:  The time to wait after middle-clicking the element. If not passed the default value found in the config is used.timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

Only used if `locator` is passed.

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

______________________________________________________________________

### method `print_tree`

**Source:** [`_control_element.py:623`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L623)

```python
print_tree(
    stream=None,
    show_properties: bool = False,
    max_depth: int = 8
) → None
```

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
windows.find("Calculator > path:2|3").print_tree()
```

______________________________________________________________________

### method `right_click`

**Source:** [`_control_element.py:864`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L864)

```python
right_click(
    locator: Optional[str] = None,
    wait_time: Optional[float] = None,
    timeout: Optional[float] = None
) → ControlElement
```

Right-clicks an element using the mouse.

**Args:**

- <b>`locator`</b>:  If given the child element which matches this locator will be right-clicked.
- <b>`wait_time`</b>:  The time to wait after right-clicking the element. If not passed the default value found in the config is used.timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

Only used if `locator` is passed.

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

______________________________________________________________________

### method `screenshot`

**Source:** [`_control_element.py:1530`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L1530)

```python
screenshot(
    filename: Union[str, Path],
    locator: Optional[str] = None,
    search_depth: int = 8,
    img_format: str = 'png',
    timeout: Optional[float] = None
) → Optional[str]
```

Take a screenshot of the element defined by the locator.

An `ActionNotPossible` exception is raised if the element doesn't allow being captured.

:param locator: String locator or element object. :param filename: Image file name/path. (can be absolute/relative) :raises ActionNotPossible: When the element can't be captured. :returns: Absolute file path of the taken screenshot image.

**Example: Robot Framework**

.. code-block:: robotframework

\*\*\* Tasks \*\*\*Take ScreenshotsScreenshot    desktop    desktop.pngScreenshot    subname:Notepad    ${OUTPUT_DIR}${/}notepad.png

**Example: Python**

.. code-block:: python

from RPA.Windows import Windowslib = Windows()

def take_screenshots():lib.screenshot("desktop", "desktop.png")lib.screenshot("subname:Notepad", "output/notepad.png")

______________________________________________________________________

### method `screenshot_pil`

**Source:** [`_control_element.py:1512`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L1512)

```python
screenshot_pil(
    locator: Optional[str] = None,
    search_depth: int = 8,
    timeout: Optional[float] = None
) → Optional[ForwardRef('Image')]
```

______________________________________________________________________

### method `select`

**Source:** [`_control_element.py:1041`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L1041)

```python
select(
    value: str,
    locator: Optional[str] = None,
    timeout: Optional[float] = None
) → ControlElement
```

Select a value on the passed element if such action is supported.

**Args:**

- <b>`value`</b>:  value to select on element.

- <b>`locator`</b>:  If given the child element which matches this locator will be used for the selection.

timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

Only used if `locator` is passed.

**Returns:**
The element used in the selection.

**Raises:**
ActionNotPossible if the element does not allow the `Select` action.

**Note:**

> This is usually used with combo box elements.

**Example:**

```python
element.select("id:FontSizeComboBox", "22")
```

______________________________________________________________________

### method `send_keys`

**Source:** [`_control_element.py:1100`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L1100)

```python
send_keys(
    keys: Optional[str] = None,
    locator: Optional[str] = None,
    interval: float = 0.01,
    wait_time: Optional[float] = None,
    send_enter: bool = False,
    timeout: Optional[float] = None
) → ControlElement
```

Sends the given keys to the element (simulates typing keys on the keyboard).

**Args:**
keys: The keys to be sent. Special keys may be sent as {Ctrl}{Alt}{Delete}, etc.

Some examples of valid key combinations are shown below:

```python
 '{Ctrl}a{Delete}{Ctrl}v{Ctrl}s{Ctrl}{Shift}s{Win}e{PageDown}'  # press Ctrl+a, Delete, Ctrl+v, Ctrl+s, Ctrl+Shift+s, Win+e, PageDown
 '{Ctrl}(AB)({Shift}(123))'  # press Ctrl+A+B, type '(', press Shift+1+2+3, type ')', if '()' follows a hold key, hold key won't release util ')'
 '{Ctrl}{a 3}'  # press Ctrl+a at the same time, release Ctrl+a, then type 'a' 2 times
 '{a 3}{B 5}'  # type 'a' 3 times, type 'B' 5 times

 - <b>`'{{}Hello{}}abc {a}{b}{c} test{} 3}{!}{a} (){(}{)}'  # type`</b>:  '{Hello}abc abc test}}}!a ()()'
'0123456789{Enter}'
'ABCDEFGHIJKLMNOPQRSTUVWXYZ{Enter}'
'abcdefghijklmnopqrstuvwxyz{Enter}'
'`~!@#$%^&*()-_=+{Enter}'

 - <b>`'[]{{}{}}\|;`</b>: '",<.>/?{Enter}'
```

- <b>`locator`</b>:  If given the child element which matches this locator will be used to send the keys.

- <b>`interval`</b>:  Time between each sent key. (defaults to 0.01 seconds)

- <b>`wait_time`</b>:  The time to wait after sending the keys to the element. If not passed the default value found in the config is used.

- <b>`send_enter`</b>:  If `True` then the {Enter} key is pressed at the end of the sent keys.

timeout: The search for a child with the given locator will be retried until the given timeout elapses.

At least one full search up to the given depth will always be done and the timeout will only take place afterwards.

If not given the global config timeout will be used.

Only used if `locator` is passed.

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

______________________________________________________________________

### method `set_focus`

**Source:** [`_control_element.py:1606`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L1606)

```python
set_focus(locator: Optional[str] = None, timeout: Optional[float] = None) → None
```

Set view focus to the element defined by the locator.

:param locator: String locator or element object.

**Example:**

.. code-block:: robotframework

Set Focus  name:Buy type:Button

______________________________________________________________________

### method `set_value`

**Source:** [`_control_element.py:1376`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L1376)

```python
set_value(
    value: str,
    locator: Optional[str] = None,
    append: bool = False,
    enter: bool = False,
    newline: bool = False,
    send_keys_fallback: bool = True,
    validator: Optional[Callable] = <function set_value_validator at 0x000002DD471E96C0>,
    timeout: Optional[float] = None
) → ControlElement
```

Set value of the element defined by the locator.

*Note:* An anchor will work only on element structures where you can rely on the stability of that root/child element tree, as remaining the same. Usually these kind of structures are tables. (but not restricted to)

*Note:* It is important to set `append=${True}` if you want to keep the current text in the element. Other option is to read the current text into a variable, then modify that value as you wish and pass it to the `Set Value` keyword for a complete text replacement. (without setting the `append` flag)

The following exceptions may be raised:

```
- ``ActionNotPossible`` if the element does not allow the `SetValue` actionto be run on it nor having ``send_keys_fallback=${True}``.
- ``ValueError`` if the new value to be set can't be set correctly.
```

:param locator: String locator or element object. :param value: String value to be set. :param append: `False` for setting the value, `True` for appending it. (OFF by default):param enter: Set it to `True` to press the *Enter* key at the end of the input. (nothing is pressed by default):param newline: Set it to `True` to add a new line at the end of the value. (no EOL included by default; this won't work with `send_keys_fallback` enabled):param send_keys_fallback: Tries to set the value by sending it through keys if the main way of setting it fails. (enabled by default):param validator: Function receiving two parameters post-setting, the expected and the current value, which returns `True` if the two values match. (bydefault, the keyword will raise if the values are different, set this to`None` to disable validation or pass your custom function instead):returns: The element object identified through the passed `locator`.

**Example: Robot Framework**

.. code-block:: robotframework

\*\*\* Tasks \*\*\*Set Values In NotepadSet Value   type:DataItem name:column1   ab c  # Set value to "ab c"# Press ENTER after setting the value.Set Value    type:Edit name:"File name:"    console.txt   enter=${True}

# Add newline (manually) at the end of the string. (Notepad example)Set Value    name:"Text Editor"  abc\\n# Add newline with parameter.Set Value    name:"Text Editor"  abc   newline=${True}

# Clear Notepad window and start appending text.Set Anchor  name:"Text Editor"# All the following keyword calls will use the anchor element as a#  starting point, UNLESS they specify a locator explicitly or#  `Clear Anchor` is used.${time} =    Get Time# Clears with `append=${False}`. (default)Set Value    value=The time now is ${time}# Append text and add a newline at the end.Set Value    value= and it's the task run time.   append=${True}...    newline=${True}# Continue appending and ensure a new line at the end by pressing#  the Enter key this time.Set Value    value=But this will appear on the 2nd line now....    append=${True}   enter=${True}   validator=${None}

**Example: Python**

.. code-block:: python

from RPA.Windows import Windows

lib_win = Windows()locator = "Document - WordPad > Rich Text Window"elem = lib_win.set_value(locator, value="My text", send_keys_fallback=True)text = lib_win.get_value(elem)print(text)

______________________________________________________________________

### method `update_geometry`

**Source:** [`_control_element.py:381`](https://github.com/robocorp/robo/tree/master/windows/src/robocorp/windows/_control_element.py#L381)

```python
update_geometry() → None
```

This method may be called to update the cached coordinates of the control bounds.
