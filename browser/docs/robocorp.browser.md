<!-- markdownlint-disable -->

# module `robocorp.browser`

Main module for doing browser automation with Playwright.

This library can be made available by pinning [![](https://img.shields.io/pypi/v/robocorp-browser?label=robocorp-browser)](https://pypi.org/project/robocorp-browser/) in your dependencies' configuration.

# Functions

______________________________________________________________________

## `configure`

Configures browser settings before any other method is called.

This method is optional, and if not invoked, default configurations will be used. Note that calling this method after the browser is initialized has no effect.

**Example:**

```python
browser.configure(browser_engine="firefox", slowmo=100)
```

**Args:**

- <b>`browser_engine`</b>:  Browser engine which should be used. Possible choices are `"chromium"`, `"chrome"`, `"chrome-beta"`, `"msedge"`, `"msedge-beta"`, `"msedge-dev"`, `"firefox"` and `"webkit"` (defaults to `"chromium"`).
- <b>`install`</b>:  Install browser or not. If not defined, download is only attempted if the browser fails to launch.
- <b>`headless`</b>:  If set to False the browser UI will be shown. If set to True the browser UI will be kept hidden. If unset or set to None it'll show the browser UI only if a debugger is detected.
- <b>`slowmo`</b>:  Run interactions in slow motion (number in millis).
- <b>`screenshot`</b>:  Whether to automatically capture a screenshot after each task. default="only-on-failure" choices=\["on", "off", "only-on-failure"\]
- <b>`isolated`</b>:  Used to define where the browser should be downloaded. If `True`, it'll be installed inside the isolated environment. If `False` (default) it'll be installed in a global cache folder.
- <b>`persistent_context_directory`</b>:  If a persistent context should be used, this should be the directory in which the persistent context should be stored/loaded from (it can be used to store the state of the automation to allow for sessions and cookies to be reused in a new automation).
- <b>`skip_playwright_stop`</b>:  Can be used to skip the playwright stop. Not recommended in general, only meant to be used to diagnose and workaround specific issues on the playwright stop coupled with an early `os._exit` shutdown in **robocorp-tasks**. Can cause a process leak and even a shutdown deadlock if used alone.

**Note:**

> See also: `robocorp.browser.configure_context` to change other arguments related to the browser context creation.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L25)

```python
configure(**kwargs) → None
```

______________________________________________________________________

## `configure_context`

Customizes browser context settings beyond those covered by the `configure` method.

Use this method to tailor the keyword arguments passed to `playwright.Browser.new_context` for scenarios requiring different context configurations.

**Example:**

```python
browser.configure_context(ignore_https_errors = True)
```

**Args:**

- <b>`**kwargs`</b>:  Keyword arguments supported by the `playwright.Browser.new_context` method.

**Note:**

> The changes done persist through the full session, so, new tasks which create a browser context will also get the configuration changes. If the change should not be used across tasks it's possible to call `robocorp.browser.context(...)` with the required arguments directly.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L82)

```python
configure_context(**kwargs) → None
```

______________________________________________________________________

## `page`

Provides a managed instance of the browser page to interact with.

**Example:**

```python
page = browser.page()
page.goto("https://robotsparebinindustries.com/#/robot-order")
page.click("button:text('OK')")
```

**Returns:**
The browser page to interact with.

Note that after a page is created, the same page is returned until the current task finishes or the page is closed.

If a new page is required without closing the current page use:

```python
 page = browser.context().new_page()
```

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L109)

```python
page() → Page
```

______________________________________________________________________

## `browser`

Provides a managed instance of the browser to interact with.

**Example:**

```python
browser_instance = browser.browser()
```

**Returns:**
The browser which should be interacted with.

If no browser is created yet one is created and the same one is returned on new invocations.

To customize the browser use the `configure` method (prior to calling this method).

**Raises:**

- <b>`RuntimeError`</b>:  If `persistent_context_directory` is specified in the configuration and this method is called a RuntimeError is raised (as in this case this API is not applicable as the browser and the context must be created at once and the browser can't be reused for the session).

**Note:**

> The returned browser must not be closed. It will be automatically closed when the task run session finishes.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L136)

```python
browser() → Browser
```

______________________________________________________________________

## `playwright`

Provides a managed instance of playwright to interact with.

**Example:**

```python
playwright_instance = browser.playwright()
```

**Returns:**
The playwright instance to interact with.

If no playwright instance is created yet one is created and the same one is returned on new invocations.

To customize it use the `configure` method (prior to calling this method).

Note that the returned instance must not be closed. It will be automatically closed when the task run session finishes.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L168)

```python
playwright() → Playwright
```

______________________________________________________________________

## `context`

Provides a managed instance of the browser context to interact with.

**Example:**

```python
browser_context = browser.context()
```

**Returns:**
The browser context instance to interact with.

If no browser context instance is created yet one is created and the same one is returned on new invocations.

Note that the returned instance must not be closed. It will be automatically closed when the task run session finishes.

**Note:**

> If the context is not created it's possible to customize the context arguments through the kwargs provided, by using the `configure(...)` method or by editing the `configure_context(...)` returned dict.
> If the context was already previously created the \*\*kwargs passed will be ignored.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L193)

```python
context(**kwargs) → BrowserContext
```

______________________________________________________________________

## `goto`

Changes the url of the current page (creating a page if needed).

**Example:**

```python
 page = browser.goto("https://robotsparebinindustries.com/#/robot-order")
```

**Args:**

- <b>`url`</b>:  Navigates to the provided URL.

**Returns:**
The page instance managed by the robocorp.tasks framework(it will be automatically closed when the task finishes).

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L223)

```python
goto(url: str) → Page
```

______________________________________________________________________

## `screenshot`

Takes a screenshot of the given page/element/locator and saves it to the log.

If no element is provided the screenshot will target the current page.

**Example:**

```python
locator = page.locator("#locator-by-class")
browser.screenshot(locator)
```

**Args:**

- <b>`element`</b>:  The page/element/locator which should have its screenshot taken. If not given the managed page instance will be used.
- <b>`timeout`</b>:  Maximum time in milliseconds. Defaults to `5000` (5 seconds). Pass `0` to disable timeout.
- <b>`image_type`</b>:  Specify screenshot type, defaults to `png`.
- <b>`log_level`</b>:  The level of the message ("INFO", "WARN" or "ERROR")

**Returns:**
The bytes from the screenshot.

**Note:**

> The element.screenshot can be used if the screenshot is not expected to be added to the log.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L243)

```python
screenshot(
    element: Optional[Page, ElementHandle, Locator] = None,
    timeout: int = 5000,
    image_type: Literal['png', 'jpeg'] = 'png',
    log_level: Literal['INFO', 'WARN', 'ERROR'] = 'INFO'
) → bytes
```

______________________________________________________________________

## `install`

Downloads and installs the given browser engine.

**Args:**

- <b>`browser_engine`</b>:  Browser engine which should be installed.
- <b>`force`</b>:  Force reinstall of stable browser channels.

**Note:**

> Google Chrome or Microsoft Edge installations will be installed at the default global location of your operating system overriding your current browser installation.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L296)

```python
install(browser_engine: BrowserEngine, force: bool = False)
```

# Exceptions

______________________________________________________________________

## `BrowserNotFound`

No matching browser found in the environment.

### Properties

- `message`

- `name`

- `stack`

______________________________________________________________________

## `InstallError`

Error encountered during browser install.

# Enums

______________________________________________________________________

## `BrowserEngine`

Valid browser engines for Playwright.

### Values

- **CHROMIUM** = chromium
- **CHROME** = chrome
- **CHROME_BETA** = chrome-beta
- **MSEDGE** = msedge
- **MSEDGE_BETA** = msedge-beta
- **MSEDGE_DEV** = msedge-dev
- **FIREFOX** = firefox
- **WEBKIT** = webkit
