<!-- markdownlint-disable -->

<a href="..\..\log\robocorp\log\redirect#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.log.redirect`





---

<a href="..\..\log\robocorp\log\redirect\setup_stdout_logging#L135"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `setup_stdout_logging`

```python
setup_stdout_logging(
    mode: str,
    redirect_to_console_messages: bool = True
) → Iterator[NoneType]
```

This function is responsible for setting up the needed stdout/stderr redirections (usually managed from robocorp-tasks). 

The redirections needed are: 
    - Redirect stdout and stderr to `console_messages` if  redirect_to_console_messages is True (while still printing to  the original streams). 
    - Write all the messages to the stdout if the mode is "json" or if  the mode is "" and the "RC_LOG_OUTPUT_STDOUT" is set to  one of ("1", "t", "true", "json"). 



**Args:**
  mode: 
 - <b>`""`</b>:  query the RC_LOG_OUTPUT_STDOUT value. 
 - <b>`"no"`</b>:  don't provide log output to the stdout. 
 - <b>`"json"`</b>:  provide json output to the stdout. 

redirect_to_console_messages: Whether messages sent to stdout and stderr should be redirected to console messages. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
