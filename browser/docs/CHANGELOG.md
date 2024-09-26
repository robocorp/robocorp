# Changelog

## Unreleased

## 2.3.4 - 2024-09-25

- Update dependencies

## 2.3.3 - 2024-04-08

- Update package's main README.

## 2.3.2 - 2024-03-27

- Docstrings improvements by following the Google style guide.

## 2.3.1 - 2024-03-19

- Enables compatibility with Action Server `0.1.0` by accepting **robocorp-tasks**
  `3.x.x`.

## 2.3.0 - 2024-03-07

- Improved browser CLI installations by enhancing SSL with truststore injection.

## 2.2.3 - 2024-02-01

- Notice in the docs about the need to include `robocorp-browser` dependency in order
  to make it available in the environment. (not included by default in `robocorp`)

## 2.2.2 - 2024-01-14

- Fix main README and update docs.

## 2.2.1 - 2023-11-02

- Reverted change to issue on playwright shutdown and added option to skip
  the playwright stop and do an early os._exit on `robocorp-tasks` as
  the previous fix didn't address the issue as expected.

## 2.2.0 - 2023-10-27

- When browsers are installed with playwright additional logging is added.
- Fixed issue where shutting down playwright could lead to a halting condition inside of `asyncio`.
- It's now possible to configure the browser to launch with a persistent context
  directory (i.e.: `launch_persistent_context`) by specifying a `persistent_context_directory`
  in the configuration.

    ```python
    from robocorp import browser
    browser.configure(
        persistent_context_directory="<path to directory>"
    )
    ```


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

- Added more information in thrown errors.

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
