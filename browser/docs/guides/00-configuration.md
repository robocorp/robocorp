# Browser configuration

Before a Playwright browser is started, it can be configured within the
executing code.

## Example

```python
from robocorp import browser

# Always use a headless Firefox browser
browser.configure(
	browser_engine="firefox",
	headless=True,
)
```

## Options

### `browser_engine`
   
Browser engine which should be used.

Valid values:
- chromium (default)
- chrome
- chrome-beta
- msedge
- msedge-beta
- msedge-dev
- firefox
- webkit

### `headless`

Run the browser in headless mode.

If not defined (or value is `None`), the browser will automatically detect
if it is an environment without a valid display device.

### `slowmo`

Run interactions in slow motion, represented in milliseconds.

### `screenshot`

Automatically capture a screenshot after each task.

Valid values:
- on
- off
- only-on-failure


### `install`

Install browser before starting. If not defined, download is only
attempted if the browser fails to launch.


### `isolated`

Used to define where the browser should be downloaded. If `True`, it'll be installed 
inside the isolated environment. If `False` (default) it'll be installed in a global cache folder.


### `persistent_context_directory`

If a persistent context should be used, this should be the directory in which 
the persistent context should be stored/loaded from (it can be used to store 
the state of the automation to allow for sessions and cookies to be reused in a
new automation).

See: [Persistent Context Directory Guide](https://github.com/robocorp/robocorp/blob/master/browser/docs/guides/01-persistent-context.md)
