<!-- markdownlint-disable -->

# module `robocorp.log.console`

**Source:** [`console.py:0`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/console.py#L0)

## Variables

- **COLOR_BLACK**
- **COLOR_BLUE**
- **COLOR_CYAN**
- **COLOR_GREEN**
- **COLOR_MAGENTA**
- **COLOR_RED**
- **COLOR_WHITE**
- **COLOR_YELLOW**

______________________________________________________________________

## function `set_color`

**Source:** [`console.py:215`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/console.py#L215)

```python
set_color(foreground_color: str) → _OnExitContextManager
```

To be used as:

with set_color(COLOR_BLACK): ...

**Args:**
foreground_color: The foreground color to be set (see COLOR_XXX constants).

______________________________________________________________________

## function `set_mode`

**Source:** [`console.py:229`](https://github.com/robocorp/robocorp/tree/master/log/src/robocorp/log/console.py#L229)

```python
set_mode(mode: str) → None
```

Can be used to set the mode of the console. Options: "auto": uses the default console"plain": disables colors"ansi": forces ansi color mode
