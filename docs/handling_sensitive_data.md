## Handling sensitive data

By default `Robot Framework Output Stream` will show information for all the `Keyword` calls as well as the parameters passed to methods.
This is very handy but comes with the drawback that some care must be must be taken in order for sensitive data to be kept out of the logs.

The most common use cases and APIs are explained below:

Usernames and passwords
------------------------

For usernames and passwords, the preferred approach is that the provider of the sensitive information
asks for the information and requests `Robot Framework Output Stream` to keep such information out of
the logs.

The usage for the API is:

```python

password = request_password()

import robocorp_logging
robocorp_logging.hide_from_output(password)
```

By calling the `hide_from_output` method, any further occurrence of the `password` contents will be
automatically changed to `<redacted>`.

Note that any variable in Robot Framework assigned to a variable which has `password` or `passwd` in
its name is also automatically redacted.

In the example below, the contents of the `${user password}` variable will be automatically added to
the list of strings to be hidden from the output.

```robotframework

*** Keyword ***
Check handling of password
    ${user password}=    Obtain password

    # The contents of ${user password} will be shown as `<redacted>` in the log.
    Log    ${user password}
```


Sensitive data obtained from APIs
----------------------------------

When handling sensitive data from APIs (such as private user information obtained from an API, as the SSN
or medical data) the preferred API is disabling the logging for variables.

This can be done either through a `log:ignore-variables` tag in the related keyword 
(which may be preferred as the stop/start is managed) or through the
`Stop logging variables`, `Start logging variables` APIs.

Example using tag:

```robotframework

*** Keyword ***
Handle sensitive info
    [Tags]    log:ignore-variables
    # Obtain and handle sensitive info

```

Example using API:

```robotframework

*** Settings ***
Library     robocorp_logging

*** Keyword ***
Handle sensitive info
    Stop logging variables
    TRY
        # Obtain and handle sensitive info
        
    FINALLY
        Start logging variables
    END


```


If even the methods called could be used to compromise some information, it's possible
to completely stop the logging with the `log:ignore-methods` tag or through the
`Stop logging methods` and `Start logging methods` APIs. 

Note: this may make debugging a failure harder as keyword calls won't be logged, 
albeit you may still call `Log` with a log level of `WARN, FAIL or ERROR` to explicitly log something in this case.

Example using tag:

*** Keyword ***
Handle sensitive info
    [Tags]    log:ignore-methods
    # Obtain and handle sensitive info

```

Example using API:

```robotframework

*** Settings ***
Library     robocorp_logging

*** Keyword ***
Handle sensitive info
    Stop logging methods
    TRY
        # Obtain and handle sensitive info
        Log     This will appear    level=WARN
        Log     This will not appear
        
    FINALLY
        Start logging methods
    END


```


