<!-- markdownlint-disable -->

<a href="../../log/src/robocorp/log/console.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.log.console`




**Variables**
---------------
- **COLOR_BLACK**
- **COLOR_BLUE**
- **COLOR_CYAN**
- **COLOR_GREEN**
- **COLOR_MAGENTA**
- **COLOR_RED**
- **COLOR_WHITE**
- **COLOR_YELLOW**

---

<a href="../../log/src/robocorp/log/console.py#L215"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `set_color`

```python
set_color(foreground_color: str) → _OnExitContextManager
```

To be used as: 

with set_color(COLOR_BLACK): ... 



**Args:**
 foreground_color:  The foreground color to be set (see COLOR_XXX constants). 


---

<a href="../../log/src/robocorp/log/console.py#L229"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `set_mode`

```python
set_mode(mode: str) → None
```

Can be used to set the mode of the console. Options: "auto": uses the default console "plain": disables colors "ansi": forces ansi color mode 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
