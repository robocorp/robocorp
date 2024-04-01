# robocorp-log

`robocorp-log` is a library which provides comprehensible logging for Python with a focus on Python automation, where detailed information on what happened and why a failure occurs is of vital importance.

> Note: The format of the log is not a part of the API and should  not be relied upon as it can change even between minor versions.

## Why

Although Python logging is flexible it may be hard to analyze the logging afterwards and visualize it. Also, the format may end up using a big amount of disk space and it may be tedious to add logging calls to all places of interest.

## How

`robocorp-log` improves those aspects by using a structured format which enables using less disk space while also providing a viewer (`log.html`) for the generated content.

Also, it provides utilities to setup logging so that logging is done automatically without having to explicitly add calls to add content to the logging (although it's still possible to do so when needed).

### Usage

It's recommended that `robocorp-log` is used through `robocorp-tasks` as `robocorp-tasks` will configure `robocorp-log` in a streamlined way, where you just need to worry about marking the entry point method with a `@tasks` decorator and it'll automatically setup the auto-logging and provide the log result in `output/log.html`.

#### Configuring with pyproject.toml

`robocorp-tasks` takes care of customizing `robocorp-log` through `pyproject.toml`.  
See the `robocorp-tasks` project for more information (`robocorp-log` only provides the core logging structure and different libraries may customize it in different ways).

Although the setup is done through `robocorp-tasks`, there are still some APIs in `robocorp.log` which are interesting to use such as:

- Utility methods to add a log message as `critical`, `warn`, `info`, `debug`, `exception`

- Utility method to add an `html` message (using the `html` method). Note that the `html` method is tested for images with base64 contents in the `log.html`, other structures must be manually checked as they can break the layout. Also, keep in mind that the provided html will be sanitized.
  
- Supressing logging through `suppress_variables`, `suppress_methods`, `suppress`.

- Hiding sensitive data (automatically based on variable or argument names with names registered in `add_sensitive_variable_name` and `add_sensitive_variable_name_pattern`) or by passing the value to be hidden to `hide_from_output`.
  
### Caveats

The auto import mode is done by having a pre-import hook which will change the AST at runtime. This mostly works, but there are a couple of caveats to keep in mind:

1. Debuggers may end up stepping into the `robocorp-log` code in
many places even if such code isn't in the source code (you may want to configure the debugger you're using to skip calls into `robocorp.log` as that's usually just an implementation detail).

2. The logging needs to be fully setup prior to importing any module that should be automatically logged.

3. Working with coroutines (`async`, `await` and `greenlet`) is not supported.

## Guides

- [Dealing with sensitive data](https://github.com/robocorp/robocorp/blob/master/log/docs/guides/00-sensitive-data.md)
- [The `.robolog` format](https://github.com/robocorp/robocorp/blob/master/log/docs/guides/01-robolog-format.md)

## API Reference

Explore our [API](https://github.com/robocorp/robocorp/blob/master/log/docs/api/README.md) for extensive documentation.

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/log/docs/CHANGELOG.md).
