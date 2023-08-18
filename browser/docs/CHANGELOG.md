# Changelog

## UNRELEASED

- When browsers are installed with playwright additional logging is added.

## 2.1.0 - 2023-08-04

- It's now possible to configure the keyword arguments used to create the playwright browser context with:
    `robocorp.browser.configure_context(**kwargs)` 
    or when creating the context with:
    `robocorp.browser.context(**kwargs)`
  
## 2.0.1 - 2023-07-14

- Fixes in the README with comments on the new `headless` behavior.

## 2.0.0 - 2023-07-14

- Backward-compatability change: behaviour of `headless` changed to the following:
    - If the `RPA_HEADLESS_MODE` environment variable is set to `1` or `0`, it overrides any headless setting.
    - If the `headless` setting is unset (or set to `None`), the headless is automatically computed so that
      the UI is shown (i.e.: headless=False) unless running in a Linux VM where the `DISPLAY` or `WAYLAND_DISPLAY` is not set.

## 1.0.2 - 2023-06-28

- Updated dependency on `robocorp-tasks` to `>=1,<3`.

## 1.0.1 - 2023-06-13

- Updated dependency on `robocorp-tasks` to `^1`.

## 0.4.4 - 2023-06-05

- Updated dependency on `robocorp-tasks` to `^0.4`.

## 0.4.3 - 2023-06-05

- Updated dependency on `robocorp-tasks` to `^0.3`.

## 0.4.2 - 2023-05-25

- Updated dependency on `robocorp-tasks` to `0.3.0`.

## 0.4.1 - 2023-05-19

- Added more information in thrown errors

## 0.4.0 - 2023-05-10

- New APIs to handle managed instances through the following APIs:
    - `configure()`: configures the default settings used to create the browser.
        - must be called prior to actually calling other APIs.
    - `page()`: gets the current page (creates if needed)
    - `browser()`: gets the current browser (creates if needed)
    - `playwright()`: gets the playwright instance (creates if needed)
    - `context()`: gets the current browser context (creates if needed)
    - `screenshot()`: takes a screenshot and puts contents in the log
- Now requires `robocorp-tasks` and `robocorp-log`.
- The version is now available in `robocorp.browser.__version__`.
