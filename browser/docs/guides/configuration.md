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

### `install`

Install browser before starting. If not defined, download is only
attempted if the browser fails to launch.

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
