## Handling sensitive data

By default `Robocorp Logging` will show information for all method calls in user
code as well as some selected libraries automatically.

This is very handy but comes with the drawback that some care must be must be taken 
in order for sensitive data to be kept out of the logs.

The most common use cases and APIs are explained below:

Usernames and passwords
------------------------

For usernames and passwords, the preferred approach is that the provider of the sensitive information
asks for the information and requests `Robocorp Logging` to keep such information out of
the logs.

The usage for the API is:

```python

password = request_password()

import robocorp_logging
robocorp_logging.hide_from_output(password)
```

By calling the `hide_from_output` method, any further occurrence of the `password` contents will be
automatically changed to `<redacted>`.

Note that any argument named `password` or `passwd` in its name is also automatically redacted.

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

This can be done with the `stop_logging_variables` API (which is usable as a context manager).

Example using API:

```python

def handle_sensitive_info()
    with stop_logging_variables():
        ...

```


If even the methods called could be used to compromise some information, it's possible
to completely stop the logging with the `stop_logging_methods` APIs. 

Note: this may make debugging a failure harder as keyword calls won't be logged, 
albeit you may still call `log` with a log level of `WARN, FAIL or ERROR` to explicitly log something in this case.

Example using API:

```python

def handle_sensitive_info()
    with stop_logging_methods():
        ...

```


