## Logging customization

Following the `Getting Started` section should be sufficient to get comprehensive 
logging for all user code executed and calls into libraries in site-packages and python libs
(which by default are configured to show just when called from user code and will
not show internal calls inside the library itself).

It's possible to change how libraries or user code is logged by customizing `log_filter_rules`
by creating a `[tool.robocorp.log]` in `pyproject.toml`.

There are three different logging configurations that may be applied for each module:

- `exclude`: excludes a module from logging.
- `full_log` (default for user code): logs a module with full information, such as method calls, arguments, yields, local assigns, and more.
- `log_on_project_call` (default for library code -- since 2.0): logs only method calls, arguments, return values and exceptions, but only when a library method is called from user code. This configuration is meant to be used for libraries (modules in site-packages or python lib) logging.

Example showing how to exclude from logging any user module which ends with `producer`:

```
[tool.robocorp.log]

log_filter_rules = [
    {name = "*producer", kind = "exclude"},
]
```

By default libraries in site-packages and python lib will be configured as `log_on_project_call`, but
it's possible to change its default through `default_library_filter_kind`.

Example of `pyproject.toml` where the `rpaframework` and `selenium` 
libraries are configured to be logged and all other libraries in site-packages/python lib are
excluded by default:

```
[tool.robocorp.log]

log_filter_rules = [
    {name = "RPA", kind = "log_on_project_call"},
    {name = "selenium", kind = "log_on_project_call"},
    {name = "SeleniumLibrary", kind = "log_on_project_call"},
]

default_library_filter_kind = "exclude"
```

Note that when specifying a module name to match in `log_filter_rules`, 
the name may either match exactly or the module name must start with the 
name followed by a dot.

This means that, for example, `RPA` would match `RPA.Browser`,
but not `RPAmodule` nor `another.RPA`.

As of `robocorp-tasks 2.0`, it's also possible to use `fnmatch` style names
(where `*` matches anything and `?` matches any single char -- see: https://docs.python.org/3/library/fnmatch.html for more information).

i.e.:

```
[tool.robocorp.log]

log_filter_rules = [
    {name = "proj.*", kind = "full_log"},
    {name = "proj[AB]", kind = "full_log"},
]
```

Note that the order of the rules is important as rules which appear
first are matched before the ones that appear afterwards.