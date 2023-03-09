# Logging for python based Robocorp projects

A logging which focused on RPA projects for Robocorp robots.

> Note: The current version is still pre-alpha and the [format specified](/docs/format.md) may still change.

## Why

Although the python logging is flexible it may be hard to analyze the logging afterwards and
provide a nice representation. Also, the format may end up using a big amount of disk space.

`robocorp-logging` improves those aspects by using a structured format which enables using less disk space
while also providing a viewer for the generated content.

Also, it provides utilities to setup logging so that logging is done automatically without having
to explicitly add calls to add content to the logging.


### Installation

Install with:

`pip install robocorp-logging`


## Dealing with sensitive data in the logs

* See: [Handling Sensitive Data](/docs/handling_sensitive_data.md)


## How

The "how" of the solution is essentially the listener arguments, data format and the parsers:

* [Format specification](/docs/format.md)
* [Listener arguments](/docs/arguments.md)
