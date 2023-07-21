# robocorp-log

`robocorp-log` is a library which provides comprehensible logging for Python with 
a focus on Python automation, where detailed information on what happened and why a
failure occurs is of vital importance.

> Note: The format of the log is not a part of the API and should  not be relied
> upon as it can change even between minor versions.

## Why

Although Python logging is flexible it may be hard to analyze the logging afterwards
and visualize it. Also, the format may end up using a big amount of disk space
and it may be tedious to add logging calls to all places of interest.

## How

`robocorp-log` improves those aspects by using a structured format which enables using less disk space
while also providing a viewer (`log.html`) for the generated content.

Also, it provides utilities to setup logging so that logging is done automatically without having
to explicitly add calls to add content to the logging (although it's still possible to do so
when needed).

### Usage

It's recommended that `robocorp-log` is used through `robocorp-tasks` as 
`robocorp-tasks` will configure `robocorp-log` in a streamlined way,
where you just need to worry about marking the entry point method with a `@tasks`
decorator and it'll automatically setup the auto-logging and provide the
log result in `output/log.html`.

`robocorp-tasks` also takes care of customizing `robocorp-log` through `pyproject.toml`.
See `robocorp-tasks` for more information.

Although the setup is done through `robocorp-tasks`, there are still
some APIs in `robocorp.log` which are interesting to use such as:

- Utility methods to add a log message as `critical`, `warn`, `info`, `debug`, `exception`
  (note that it's possible to embed html by passing `html=True` in those methods,
  so, things as screenshots can be directly embedded into the log).
  
- Supressing logging through `suppress_variables`, `suppress_methods`, `suppress`.

- Hiding sensitive data (automatically based on variable or argument names with
  names registered in `add_sensitive_variable_name` and `add_sensitive_variable_name_pattern`)
  or by passing the value to be hidden to `hide_from_output`.
  
### Caveats

The auto import mode is done by having a pre-import hook which will change the AST
at runtime. This mostly works, but there are a couple of caveats to keep in mind:

1. Debuggers may end up stepping into the `robocorp-log` code in
many places even if such code isn't in the source code (you may want to configure 
the debugger you're using to skip calls into `robocorp.log` as that's usually
just an implementation detail).

2. The logging needs to be fully setup prior to importing any module that should 
be automatically logged.

3. Working with coroutines (`async`, `await` and `greenlet`) is not supported.

## Guides

- [Dealing with sensitive data](./guides/sensitive-data.md)
- [The `.robolog` format](./guides/robolog-format.md)

## API Reference

Information on specific functions or classes: [robocorp.log](./api/robocorp.log.md)

## Changelog

A list of releases and corresponding changes can be found in the [changelog](./CHANGELOG.md).
