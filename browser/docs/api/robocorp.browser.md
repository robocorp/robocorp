<!-- markdownlint-disable -->

# module `robocorp.browser`

**Source:** [`__init__.py:0`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L0)

Main module for doing browser automation with Playwright.

This library can be made available by pinning ![](https://img.shields.io/pypi/v/robocorp-browser?label=robocorp-browser) in your dependencies' configuration.

______________________________________________________________________

## function `configure`

**Source:** [`__init__.py:26`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L26)

```python
configure(**kwargs) → None
```

May be called before any other method to configure the browser settings.

Calling this method is optional (if not called a default configuration will be used -- note that calling this method after the browser is already initialized will have no effect).

**Args:**
browser_engine: Browser engine which should be used default="chromium" choices=\["chromium", "chrome", "chrome-beta", "msedge", "msedge-beta", "msedge-dev", "firefox", "webkit"\]

install: Install browser or not. If not defined, download is only attempted if the browser fails to launch.

- <b>`headless`</b>:  If set to False the browser UI will be shown. If set to True the browser UI will be kept hidden. If unset or set to None it'll show the browser UI only if a debugger is detected.

slowmo: Run interactions in slow motion (number in millis).

- <b>`screenshot`</b>:  Whether to automatically capture a screenshot after each task. Options are `on`, `off`, and `only-on-failure` (default).

isolated: Used to define where the browser should be downloaded. If `True`, it'll be installed inside the isolated environment. If `False` (default) it'll be installed in a global cache folder.

persistent_context_directory: If a persistent context should be used, this should be the directory in which the persistent context should be stored/loaded (it can be used to store the state of the automation to allow for sessions and cookies to be reused in a new automation).

- <b>`viewport_size`</b>:  Size to be set for the viewport. Specified as tuple(width, height).

skip_playwright_stop: Can be used to skip the playwright stop. Not recommended in general, only meant to be used to diagnose and workaround specific issues on the playwright stop coupled with an early os.\_exit shutdown in `robocorp-tasks`. Can cause a process leak and even a shutdown deadlock if used alone.

**Note:**

> See also: `robocorp.browser.configure_context` to change other arguments related to the browser context creation.

______________________________________________________________________

## function `configure_context`

**Source:** [`__init__.py:95`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L95)

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

> The changes done persist through the full session, so, new tasks which create a browser context will also get the configuration changes. If the change should not be used across tasks it's possible to call `robocorp.browser.context(...)` with the required arguments directly.

______________________________________________________________________

## function `page`

**Source:** [`__init__.py:123`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L123)

```python
page() → Page
```

Provides a managed instance of the browser page to interact with.

**Returns:**
The browser page to interact with.

Note that after a page is created, the same page is returned until the current task finishes or the page is closed.

If a new page is required without closing the current page use:

```python
 from robocorp import browser
 page = browser.context().new_page()
```

______________________________________________________________________

## function `browser`

**Source:** [`__init__.py:145`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L145)

```python
browser() → Browser
```

Provides a managed instance of the browser to interact with.

**Returns:**
The browser which should be interacted with.

If no browser is created yet one is created and the same one is returned on new invocations.

To customize the browser use the `configure` method (prior to calling this method).

Note that the returned browser must not be closed. It will be automatically closed when the task run session finishes.

**Raises:**
RuntimeError: If `persistent_context_directory` is specified in the configuration and this method is called a RuntimeError is raised (as in this case this API is not applicable as the browser and the context must be created at once and the browser can't be reused for the session).

______________________________________________________________________

## function `playwright`

**Source:** [`__init__.py:173`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L173)

```python
playwright() → Playwright
```

Provides a managed instance of playwright to interact with.

**Returns:**
The playwright instance to interact with.

If no playwright instance is created yet one is created and the same one is returned on new invocations.

To customize it use the `configure` method (prior to calling this method).

Note that the returned instance must not be closed. It will be automatically closed when the task run session finishes.

______________________________________________________________________

## function `context`

**Source:** [`__init__.py:194`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L194)

```python
context(**kwargs) → BrowserContext
```

Provides a managed instance of the browser context to interact with.

**Returns:**
The browser context instance to interact with.

If no browser context instance is created yet one is created and the same one is returned on new invocations.

Note that the returned instance must not be closed. It will be automatically closed when the task run session finishes.

**Note:**

> If the context is not created it's possible to customize the context arguments through the kwargs provided, by using the `configure(...)` method or by editing the `configure_context(...)` returned dict.
> If the context was already previously created the \*\*kwargs passed will be ignored.

______________________________________________________________________

## function `goto`

**Source:** [`__init__.py:220`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L220)

```python
goto(url: str) → Page
```

Changes the url of the current page (creating a page if needed).

**Args:**

- <b>`url`</b>:  Navigates to the provided URL.

**Returns:**
The page instance managed by the robocorp.tasks framework(it will be automatically closed when the task finishes).

______________________________________________________________________

## function `screenshot`

**Source:** [`__init__.py:236`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L236)

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

- <b>`element`</b>:  The page/element/locator which should have its screenshot taken. If notgiven the managed page instance will be used.

**Returns:**
The bytes from the screenshot.

______________________________________________________________________

## function `install`

**Source:** [`__init__.py:279`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/__init__.py#L279)

```python
install(browser_engine: BrowserEngine, force: bool = False)
```

Downloads and installs the given browser engine.

Note: Google Chrome or Microsoft Edge installations will be installed at the default global location of your operating system overriding your current browser installation.

**Args:**

- <b>`browser_engine`</b>:  Browser engine which should be installed

______________________________________________________________________

## enum `BrowserEngine`

**Source:** [`_types.py:14`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/_types.py#L14)

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

______________________________________________________________________

## exception `InstallError`

**Source:** [`_types.py:10`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/_types.py#L10)

Error encountered during browser install.

______________________________________________________________________

## exception `BrowserNotFound`

**Source:** [`_types.py:6`](https://github.com/robocorp/robocorp/tree/master/browser/src/robocorp/browser/_types.py#L6)

No matching browser found in the environment.

#### property `message`

#### property `name`

#### property `stack`
