<!-- markdownlint-disable -->

# module `robocorp.log.console`

# Variables

- **COLOR_BLACK**
- **COLOR_BLUE**
- **COLOR_CYAN**
- **COLOR_GREEN**
- **COLOR_MAGENTA**
- **COLOR_RED**
- **COLOR_WHITE**
- **COLOR_YELLOW**

# Functions

______________________________________________________________________

## `set_color`

To be used as:

with set_color(COLOR_BLACK): ...

**Args:**

- <b>`foreground_color`</b>:  The foreground color to be set (see COLOR_XXX constants).

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/console.py#L215)

```python
set_color(foreground_color: str) → _OnExitContextManager
```

______________________________________________________________________

## `set_mode`

Can be used to set the mode of the console. Options: "auto": uses the default console"plain": disables colors"ansi": forces ansi color mode

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/console.py#L229)

```python
set_mode(mode: str) → None
```
