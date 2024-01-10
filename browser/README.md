# robocorp-browser

The `robocorp-browser` is a wrapper for the [Playwright](https://playwright.dev/python/)
project, with quality-of-life improvements such as automatic lifecycle management
for Playwright objects (meant to be used with `robocorp-tasks`).

## Getting started

```python
from robocorp.tasks import task
from robocorp import browser
from robocorp import vault


@task
def browser_automate():
    # Configure may be used to set the basic robocorp.browser settings.
    # It must be called prior to calling APIs which create playwright objects.
    browser.configure(
        # Note: screenshot="only-on-failure" is actually the default.
        # If the browser_automate() function finishes with an exception it will
        # make a screenshot and embed it into the logs.
        screenshot="only-on-failure",
        
        # By default headless is False unless running in a Linux container
        # without a DISPLAY/WAYLAND_DISPLAY environment variable, but it
        # can also be manually specified.
        headless=True,
        
        # Interactions may be run in slow-motion (given in milliseconds).
        slowmo=100,
    )

    # browser.goto() may be used as a shortcut to get the current page and
    # go to some url (it may create the browser if still not created).
    browser.goto("https://example.com>")

    login()


def login():
    # APIs in robocorp.browser return the same browser instance, which is
    # automatically closed when the task finishes.
    page = browser.page()

    # robocorp.vault is recommended for managing secrets.
    account = vault.get_secret("default-account")

    # Use the playwright Browser api as usual.
    page.fill('//input[@ng-reflect-name="password"]', account["password"])
    page.click("input:text('Submit')")
```

## Guides

- [Browser configuration](https://github.com/robocorp/robocorp/blob/master/browser/docs/guides/00-configuration.md)
- [Persistent Context](https://github.com/robocorp/robocorp/blob/master/browser/docs/guides/01-persistent-context.md)

## API Reference

Information on specific functions or classes: [robocorp.browser](https://github.com/robocorp/robocorp/blob/master/browser/docs/api/robocorp.browser.md)

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/browser/docs/CHANGELOG.md).
