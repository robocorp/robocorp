<!-- markdownlint-disable -->

# API Overview

## Modules

- [`robocorp.browser`](./robocorp.browser.md#module-robocorpbrowser): Main module for doing browser automation with Playwright.
- [`robocorp.browser.cli`](./robocorp.browser.cli.md#module-robocorpbrowsercli)

## Classes

- [`_types.BrowserEngine`](./robocorp.browser._types.md#class-browserengine): Valid browser engines for Playwright.
- [`_types.BrowserNotFound`](./robocorp.browser._types.md#class-browsernotfound): No matching browser found in the environment.
- [`_types.InstallError`](./robocorp.browser._types.md#class-installerror): Error encountered during browser install.

## Functions

- [`browser.browser`](./robocorp.browser.md#function-browser): Provides a managed instance of the browser to interact with.
- [`browser.configure`](./robocorp.browser.md#function-configure): Configures browser settings before any other method is called.
- [`browser.configure_context`](./robocorp.browser.md#function-configure_context): Customizes browser context settings beyond those covered by the `configure` method.
- [`browser.context`](./robocorp.browser.md#function-context): Provides a managed instance of the browser context to interact with.
- [`browser.goto`](./robocorp.browser.md#function-goto): Changes the url of the current page (creating a page if needed).
- [`browser.install`](./robocorp.browser.md#function-install): Downloads and installs the given browser engine.
- [`browser.page`](./robocorp.browser.md#function-page): Provides a managed instance of the browser page to interact with.
- [`browser.playwright`](./robocorp.browser.md#function-playwright): Provides a managed instance of playwright to interact with.
- [`browser.screenshot`](./robocorp.browser.md#function-screenshot): Takes a screenshot of the given page/element/locator and saves it to the log.
- [`cli.main`](./robocorp.browser.cli.md#function-main)
