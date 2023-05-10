<!-- markdownlint-disable -->

<a href="..\..\browser\src\robocorp\browser\__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.browser`





---

<a href="..\..\browser\src\robocorp\browser\__init__.py#L6"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `configure`

```python
configure(**kwargs) → None
```

May be called before any other method to configure the browser settings. 

Calling this method is optional (if not called a default configuration will be used -- note that calling this method after the browser is already initialized will have no effect). 



**Args:**
  browser_engine:  help="Browser engine which should be used",  choices=["chrome", "firefox"], 


 - <b>`headless`</b>:  If set to False the browser UI will be shown. If set to True  the browser UI will be kept hidden. If unset or set to None it'll  show the browser UI only if a debugger is detected. 

slowmo:  Run interactions in slow motion. 

screenshot:  default="only-on-failure",  choices=["on", "off", "only-on-failure"],  help="Whether to automatically capture a screenshot after each task.", 


---

<a href="..\..\browser\src\robocorp\browser\__init__.py#L41"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `page`

```python
page() → Page
```

Provides a managed instance of the browser page to interact with. 



**Returns:**
  The browser page to interact with. 

 Note that after a page is created, the same page is returned until the  current task finishes or the page is closed. 

 If a new page is required without closing the current page use: 

 from robocorp import browser  page = browser.context.new_page() 


---

<a href="..\..\browser\src\robocorp\browser\__init__.py#L61"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `browser`

```python
browser() → Browser
```

Provides a managed instance of the browser to interact with. 



**Returns:**
  The browser which should be interacted with. 

 If no browser is created yet one is created and the same one  is returned on new invocations. 

 To customize the browser use the `configure` method (prior  to calling this method). 

 Note that the returned browser must not be closed. It will be  automatically closed when the task run session finishes. 


---

<a href="..\..\browser\src\robocorp\browser\__init__.py#L82"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `playwright`

```python
playwright() → Playwright
```

Provides a managed instance of playwright to interact with. 



**Returns:**
  The playwright instance to interact with. 

 If no playwright instance is created yet one is created and the same one  is returned on new invocations. 

 To customize it use the `configure` method (prior  to calling this method). 

 Note that the returned instance must not be closed. It will be  automatically closed when the task run session finishes. 


---

<a href="..\..\browser\src\robocorp\browser\__init__.py#L103"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `context`

```python
context() → BrowserContext
```

Provides a managed instance of the browser context to interact with. 



**Returns:**
  The browser context instance to interact with. 

 If no browser context instance is created yet one is created and the  same one is returned on new invocations. 

 To customize it use the `configure` method (prior  to calling this method). 

 Note that the returned instance must not be closed. It will be  automatically closed when the task run session finishes. 


---

<a href="..\..\browser\src\robocorp\browser\__init__.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `open_browser`

```python
open_browser(
    browser_engine: Literal['firefox', 'chrome'] = 'chrome',
    headless: Optional[bool] = None
) → Browser
```

Shortcut to configure and launch a browser instance (using Playwright). 

Note that if the browser was already previously launched the previous instance will be returned and any configuration passed will be ignored. 



**Args:**
 
 - <b>`browser_engine`</b>:  Specifies which browser to use. Supported browsers are:  ``chrome`` and ``firefox``. 


 - <b>`headless`</b>:  If set to False the browser UI will be shown. If set to True  the browser UI will be kept hidden. If unset or set to None it'll  show the browser UI only if a debugger is detected. 



**Note:**

> The arguments related to browser initialization will only be used if this is the first call, on subsequent calls the same browser instance will be used and the current page will open the given url. 
>

**Returns:**
 The browser instance. 


---

<a href="..\..\browser\src\robocorp\browser\__init__.py#L153"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `open_url`

```python
open_url(
    url: str,
    browser_engine: Literal['firefox', 'chrome'] = 'chrome',
    headless: Optional[bool] = None
) → Page
```

Changes the url of the current page (creating a page if needed). 



**Args:**
 
 - <b>`url`</b>:  Navigates to the provided URL. 


 - <b>`browser`</b>:  Specifies which browser to use. Supported browsers are:  ``chrome`` and ``firefox``. 


 - <b>`headless`</b>:  If set to False the browser UI will be shown. If set to True  the browser UI will be kept hidden. If unset or set to None it'll  show the browser UI only if a debugger is detected. 



**Note:**

> The arguments related to browser initialization will only be used if this is the first call, on subsequent calls the same browser instance will be used and the current page will open the given url. 
>

**Returns:**
 The page instance managed by the robocorp.tasks framework (it will be automatically closed when the task finishes). 


---

<a href="..\..\browser\src\robocorp\browser\__init__.py#L186"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `screenshot`

```python
screenshot(
    page: Optional[Page] = None,
    timeout: int = 5000,
    image_type: Literal['png', 'jpeg'] = 'png',
    log_level: Literal['INFO', 'WARN', 'ERROR'] = 'INFO'
) → bytes
```

Takes a screenshot of the given page and saves it to the log. If no page is provided the current page is saved. 

Note: the page.screenshot can be used if the screenshot is not expected to be added to the log. 



**Args:**
 
 - <b>`page`</b>:  The page which should have its screenshot taken. If not given the managed page instance will be used. 



**Returns:**
 The bytes from the screenshot. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
