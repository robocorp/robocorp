# Persistent Context

It's possible to use a persistent context for automating with `robocorp-browser`.

When a persistent context is used, all the information which is obtained
during the browser interaction (such as cookies, local storage, etc) will
be saved in a specified directory and when the browser is opened afterwards,
the same information will be loaded from the given directory.

To use this feature, it's possible to use the `browser.configure` API and
pass the `persistent_context_directory` (note that this must be called before
any browser page or context is actually created).

## Example

```python
from robocorp import browser

browser.configure(
	persistent_context_directory="./persistent_context",
)

page = browser.page()
```

## Caveats

- Note: it's recommended that only a single run uses a given
  persistent context at a time as the persistent context could include
  even open pages, which can be potentially troublesome at times. 
  
  Sometimes it may be better just to save/restore the cookies (which 
  can be done using the code below):
  
  ```python
  from robocorp import browser
  import json
  
  cookies = json.dumps(browser.context().cookies())
  ... # Save to disk (or shared resource such as `Vault`) and later restore with:
  browser.context().add_cookies(json.loads(cookies))
  
- When using the persistent context, the `robocorp.windows.browser()` API will
  not be available as the browser is always created with a `context`, so,
  only `robocorp.windows.context()` is applicable.
