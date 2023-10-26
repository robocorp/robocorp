# Dealing with sensitive data

By default `Robocorp Log` will show information for all method calls in user
code as well as some selected libraries automatically.

This is very handy but comes with the drawback that some care must be must be taken 
in order for sensitive data to be kept out of the logs.

The most common use cases and APIs are explained below:

### Usernames and passwords

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

### Sensitive data obtained from APIs

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


### Specifying strings that should never be hidden

On some cases it's possible that some common string ends up being redacted
(for instance, `None` could end up being redacted or just the letter `a`).
This can make it really hard to read logs afterwards, as those strings would
be redacted everywhere.

For such circumstances it's possible to configure the logging so that redaction
of such strings doesn't happen (by default `'None', 'True', 'False' and
strings with 2 or less chars won't be redacted, but it's possible to configure
it as needed).

Example:

```python
from robocorp import log
config = log.hide_strings_config()
config.dont_hide_strings_smaller_or_equal_to = 3
config.dont_hide_strings.add('hour')
```