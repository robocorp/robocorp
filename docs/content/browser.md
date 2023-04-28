<!-- markdownlint-disable -->

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\browser\src\robo\libs\browser\browser.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `browser`




**Global Variables**
---------------
- **EXECUTABLE_PATHS**

---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\browser\src\robo\libs\browser\browser.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `open_browser`

```python
open_browser(
    browser: Literal['firefox', 'chrome'] = 'chrome',
    headless=True
) → Browser
```

Launches a Playwright browser instance. 



**Args:**
 
 - <b>`browser`</b>:  Specifies which browser to use. Supported browsers are: ``chrome`` and ``firefox``. 
 - <b>`headless`</b>:  If set to False a GUI is provided, otherwise it is hidden. 



**Returns:**
 
 - <b>`Browser`</b>:  A Browser instance. 


---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\browser\src\robo\libs\browser\browser.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `open_url`

```python
open_url(url: str, headless=True) → Page
```

Launches a Playwright browser instance and opens the given URL. 



**Note:**

> Uses the ``chrome`` browser. 
>

**Args:**
 
 - <b>`url`</b>:  Navigates to the provided URL. 
 - <b>`headless`</b>:  If set to False a GUI is provided, otherwise it is hidden. 



**Returns:**
 
 - <b>`Page`</b>:  A Page instance. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
