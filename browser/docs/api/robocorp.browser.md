<!-- markdownlint-disable -->

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.browser`





---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `configure`

```python
configure(**kwargs) → None
```

May be called before any other method to configure the browser settings. 

Calling this method is optional (if not called a default configuration will be used -- note that calling this method after the browser is already initialized will have no effect). 



**Args:**

 - <b>`browser_engine`</b>:  Browser engine which should be used (default: Chromium) 
 - <b>`headless`</b>:  If set to False the browser UI will be shown. If set to True  the browser UI will be kept hidden. If unset or set to None it'll  show the browser UI only if a debugger is detected. 
 - <b>`slowmo`</b>:  Run interactions in slow motion. 
 - <b>`screenshot`</b>:  Whether to automatically capture a screenshot after each task.  Options are `on`, `off`, and `only-on-failure` (default). 
 - <b>`viewport_size`</b>:  Size to be set for the viewport. Specified as tuple(width, height). 



**Note:**

>See also: `robocorp.browser.configure_context` to change otherarguments related to the browser context creation.


---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `configure_context`

```python
configure_context(**kwargs) → None
```

While the most common configurations may be configured through `configure`, not all arguments passed to `playwright.Browser.new_context` are covered. 

For cases where different context keyword arguments are needed it's possible to use this method to customize the keyword arguments passed to `playwright.Browser.new_context`. 



**Example:**
```python
from robocorp import browser
browser.configure_context(ignore_https_errors = True)
``` 



**Note:**

>The changes done persist through the full session, so, new tasks whichcreate a browser context will also get the configuration changes.If the change should not be used across tasks it's possibleto call `robocorp.browser.context(...)` with the required argumentsdirectly.


---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L83"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `page`

```python
page() → Page
```

Provides a managed instance of the browser page to interact with. 



**Returns:**
 The browser page to interact with. 

 Note that after a page is created, the same page is returned until the  current task finishes or the page is closed. 

 If a new page is required without closing the current page use: 

```python
 from robocorp import browser
 page = browser.context().new_page()
``` 


---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L126"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L147"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `context`

```python
context(**kwargs) → BrowserContext
```

Provides a managed instance of the browser context to interact with. 



**Returns:**
 The browser context instance to interact with. 

 If no browser context instance is created yet one is created and the  same one is returned on new invocations. 

 Note that the returned instance must not be closed. It will be  automatically closed when the task run session finishes. 



**Note:**

>If the context is not created it's possible to customize the contextarguments through the kwargs provided, by using the `configure(...)`method or by editing the `configure_context(...)` returned dict.
>If the context was already previously created the **kwargs passed willbe ignored.


---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L173"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `goto`

```python
goto(url: str) → Page
```

Changes the url of the current page (creating a page if needed). 



**Args:**

 - <b>`url`</b>:  Navigates to the provided URL. 



**Returns:**
The page instance managed by the robocorp.tasks framework (it will be automatically closed when the task finishes). 


---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L189"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `screenshot`

```python
screenshot(
    element: Optional[Page, ElementHandle, Locator] = None,
    timeout: int = 5000,
    image_type: Literal['png', 'jpeg'] = 'png',
    log_level: Literal['INFO', 'WARN', 'ERROR'] = 'INFO'
) → bytes
```

Takes a screenshot of the given page/element/locator and saves it to the log. If no element is provided the screenshot will target the current page. 

Note: the element.screenshot can be used if the screenshot is not expected to be added to the log. 



**Args:**

 - <b>`element`</b>:  The page/element/locator which should have its screenshot taken. If not given the managed page instance will be used. 



**Returns:**
The bytes from the screenshot. 


---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L232"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `install`

```python
install(browser_engine: BrowserEngine)
```

Downloads and installs the given browser engine. 

Note: Google Chrome or Microsoft Edge installations will be installed at the default global location of your operating system overriding your current browser installation. 



**Args:**

 - <b>`browser_engine`</b>:  Browser engine which should be installed 


---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/_browser_engines.py#L14"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>enum</kbd> `BrowserEngine`
Valid browser engines for Playwright. 


---
### <kbd>values</kbd>
- **CHROMIUM** = chromium
- **CHROME** = chrome
- **CHROME_BETA** = chrome-beta
- **MSEDGE** = msedge
- **MSEDGE_BETA** = msedge-beta
- **MSEDGE_DEV** = msedge-dev
- **FIREFOX** = firefox
- **WEBKIT** = webkit



