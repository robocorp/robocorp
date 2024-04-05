# robocorp-browser

The **robocorp-browser** package is a light wrapper for the [Playwright](https://playwright.dev/python/) -project, with quality-of-life improvements, such as automatic lifecycle management for Playwright objects (meant to be used with **robocorp-tasks**).

## Usage

[![`robocorp-browser`](https://img.shields.io/pypi/v/robocorp-browser?label=robocorp-browser)](https://pypi.org/project/robocorp-browser/)

> 👉 Check that you have added the dependency in your configuration; this library is not part of the [**robocorp**](https://pypi.org/project/robocorp/) bundle.
> - _conda.yaml_ for automation [Task Packages](https://robocorp.com/docs/robot-structure)
> - _package.yaml_ for automation Action Packages
> - _requirements.txt_, _pyproject.toml_, _setup.py|cfg_ etc. for the rest

```python
from robocorp import browser, vault
from robocorp.tasks import task

@task
def automate_browser():
    """Start a browser to login in the surfed page."""
    # The configuration is used to set the basic `robocorp.browser` settings.
    # It must be called before calling APIs that create Playwright objects.
    browser.configure(
        # NOTE: `screenshot="only-on-failure"` is the default.
        # If this function finishes with an exception, it will make a screenshot and
        #  embed it into the logs.
        screenshot="only-on-failure",

        # By default, `headless` is False, unless running in a Linux container
        #  without a DISPLAY/WAYLAND_DISPLAY environment variable, but it
        #  can also be manually overridden.
        headless=True,  # won't display the browser window

        # Interactions may be run in slow motion (given in milliseconds).
        slowmo=100,
    )

    # The `browser.goto()` call may be used as a shortcut to get the current page and
    #  surf some URL (it may create the browser if not created already).
    browser.goto("https://example.com>")

    _login()  # call the login instructions


def _login():
    # APIs in `robocorp.browser` return the same browser instance, which is
    #  automatically closed when the task finishes.
    page = browser.page()

    # `robocorp.vault` is recommended for managing secrets.
    account = vault.get_secret("default-account")

    # Use the Playwright Browser API as usual to interact with the web elements.
    page.fill('//input[@ng-reflect-name="password"]', account["password"])
    page.click("input:text('Submit')")
```

🚀 Get started with our [template](https://robocorp.com/portal/robot/robocorp/template-python-browser) now!

## Guides

- [Browser configuration](https://github.com/robocorp/robocorp/blob/master/browser/docs/guides/00-configuration.md)
- [Persistent Context](https://github.com/robocorp/robocorp/blob/master/browser/docs/guides/01-persistent-context.md)

## API Reference

Explore our [API](https://github.com/robocorp/robocorp/blob/master/browser/docs/api/README.md) for extensive documentation.

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/browser/docs/CHANGELOG.md).
