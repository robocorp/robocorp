<!-- markdownlint-disable -->

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.browser`





---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L244"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `install`

```python
install(browser_engine: BrowserEngine)
```

Downloads and installs the given browser engine. 

Note: Google Chrome or Microsoft Edge installations will be installed at the default global location of your operating system overriding your current browser installation. 



**Args:**
 browser_engine:  help="Browser engine which should be installed",  choices=[chromium", "chrome", "chrome-beta", "msedge", "msedge-beta", "msedge-dev", "firefox", "webkit"] 


---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L18"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `configure`

```python
configure(**kwargs) → None
```

May be called before any other method to configure the browser settings. 

Calling this method is optional (if not called a default configuration will be used -- note that calling this method after the browser is already initialized will have no effect). 



**Args:**
 browser_engine:  Browser engine which should be used  default="chromium"  choices=["chromium", "chrome", "chrome-beta", "msedge",  "msedge-beta", "msedge-dev", "firefox", "webkit"] 


 - <b>`headless`</b>:  If set to False the browser UI will be shown. If set to True  the browser UI will be kept hidden. If unset or set to None it'll  show the browser UI only if a debugger is detected. 

slowmo:  Run interactions in slow motion. 

screenshot:  Whether to automatically capture a screenshot after each task.  default="only-on-failure"  choices=["on", "off", "only-on-failure"] 

viewport_size:  Size to be set for the viewport. Specified as tuple(width, height). 



**Note:**

>See also: `robocorp.browser.configure_context` to change otherarguments related to the browser context creation.


---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L95"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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
 page = browser.context.new_page()
``` 


---

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L138"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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

<a href="https://github.com/robocorp/robo/tree/master/browser/src/robocorp/browser/__init__.py#L159"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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


