# robocorp-log

`robocorp-log` is a library which provides comprehensible logging for python with 
a focus on python automation, where detailed information on what happened and why a
failure occurs is of vital importance.

> Note: The current version (1.0.0) is now in beta. Semantic versioning is used in the project.
> Note: Please note that the format of the log is not a part of the API and should 
> not be relied upon as it can change even among minor versions.

## Why

Although the python logging is flexible it may be hard to analyze the logging afterwards and
visually analyze it. Also, the format may end up using a big amount of disk space
and it may be tedious to add logging calls to all places of interest.

## How

`robocorp-log` improves those aspects by using a structured format which enables using less disk space
while also providing a viewer (`log.html`) for the generated content.

Also, it provides utilities to setup logging so that logging is done automatically without having
to explicitly add calls to add content to the logging (although it's still possible to do so
when needed).


### Installation

Install with:

`pip install robocorp-log`


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

- Utility methods to add a log message as `critical`, `warn`, `info`, `exception`
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

3. `async` and `await` are not currently well supported (although it's already in
the plans).


## Dealing with sensitive data in the logs

By default `Robocorp Log` will show information for all method calls in user
code as well as some selected libraries automatically.

This is very handy but comes with the drawback that some care must be must be taken 
in order for sensitive data to be kept out of the logs.

The most common use cases and APIs are explained below:

Usernames and passwords
------------------------

For usernames and passwords, the preferred approach is that the provider of the sensitive information
asks for the information and requests `Robocorp Log` to keep such information out of
the logs.

The usage for the API is:

```python

from robocorp import log

with log.suppress_variables():
    pwd = request_password()
    log.hide_from_output(pwd)
```

By calling the `hide_from_output` method, any further occurrence of the `password` contents will be
automatically changed to `<redacted>`.

Note that some arguments and variable assigns for some names are automatically redacted.

-- by default `password` and `passwd`, but others may be customized through the 
`robocorp.log.add_sensitive_variable_name` and `add_sensitive_variable_name_pattern`
functions.

In the example below, the contents of the `${user password}` variable will be automatically added to
the list of strings to be hidden from the output.

```python

def check_handling(user_password):
    ...

check_handling('the password')
```


Sensitive data obtained from APIs
----------------------------------

When handling sensitive data from APIs (such as private user information obtained from an API, as the SSN
or medical data) the preferred API is disabling the logging for variables.

This can be done with the `robocorp.log.suppress_variables` API (which is usable as a context manager).

Example using API:

```python
from robocorp import log

def handle_sensitive_info()
    with log.suppress_variables():
        ...

```


If even the methods called could be used to compromise some information (or if
there's too much noise in those calls), it's possible
to completely stop the logging with the `robocorp.log.suppress` API. 

Note: this may make debugging a failure harder as method calls won't be logged, 
albeit you may still call `critical / info / warn` to explicitly log something in this case.

Example using API:

```python
from robocorp import log

def handle_sensitive_info()
    with log.suppress():
        ...

```


## Internal structure

* [Format specification](https://github.com/robocorp/robo/tree/master/log/docs/format.md)

## License: Apache 2.0
## Copyright: Robocorp Technologies, Inc.

