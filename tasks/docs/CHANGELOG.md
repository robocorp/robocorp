# Changelog

## 2.4.2 - 2023-11-09

- On early exit with `RC_OS_EXIT`, make sure that the logs are written prior to exiting.

## 2.4.1 - 2023-11-08

- Setting CoInitEx initialization parameters to prevent issue where `asyncio` would fail to shutdown.

## 2.4.0 - 2023-11-02

- `RC_DUMP_THREADS_AFTER_RUN` may be set to "0" or "false" to prevent threads from being dumped after the teardown
  (by default it'll dump threads 40 seconds after the tasks finish running, `RC_DUMP_THREADS_AFTER_RUN_TIMEOUT` may
  be used to configure a different timeout).
  
- Created an option to do an early `os._exit` after running all the tasks. It's possible to do
  an early exit with or without running the tasks teardown. When used the subprocesses are
  killed and an `os._exit` is issued with a returncode based on whether the tasks 
  failed (returncode=1) or not (returncode=0).
  To exit after all tasks finished running and after doing the teardown use: `--os-exit=after-teardown` in
  the command line or `RC_OS_EXIT=after-teardown` as an environment variable.
  To exit without doing the teardown after all tasks finished running: `--os-exit=before-teardown` in
  the command line or `RC_OS_EXIT=before-teardown` as an environment variable.
  
## 2.3.0 - 2023-10-27

- Use `truststore` for native system certificates, if available in environment

- `--teardown-dump-threads-timeout` argument can now be used to specify a timeout (in seconds) to print running threads after the teardown starts 
    - if not specified the `RC_TEARDOWN_DUMP_THREADS_TIMEOUT` may be used instead.
    - Defaults to `5` (seconds) if not specified.

- `--teardown-interrupt-timeout` argument can now be used to specify a timeout (in seconds) to interrupt the teardown process. 
    - If not specified the `RC_TEARDOWN_INTERRUPT_TIMEOUT` environment variable may also be used.

- Add support for fixtures with the new `setup` and `teardown` decorators
- Allow modifying the `status` of tasks in fixtures

## 2.2.0 - 2023-09-07

- The absolute output dir is saved before running tasks (so that changes to the `cwd` don't affect it).
- If 2 tasks are found with the same name in the same module a proper error is raised.
- Logging info sent to `ROBOCORP_TASKS_LOG_LISTENER_PORT` is written in a thread.
- The `ROBOT_ARTIFACTS` environment variable is now used for the `log.html` output dir (if available and not specified in the command line).
- Fixed issue where a module with a task with a relative import would not be imported. 
- If a directory is specified to load tasks from it, the folder __init__.py is also loaded when collecting tasks.


## 2.1.3 - 2023-07-19

- Moved some internal APIs to load the `robocorp.log` auto log configuration to the
  `robocorp.log` project public API.
- Now requires `robocorp-log = ">=2.4,<3"`


## 2.1.2 - 2023-07-10

- Fixed issue where the line number logged for the task had an off by 1 error.


## 2.1.1 - 2023-07-06

- Properly marks that `robocorp-log 2.2` onwards is required.

  
## 2.1.0 - 2023-07-06

- If a `ROBOCORP_TASKS_LOG_LISTENER_PORT` is set, it'll connect to that port
  and send details on what's happening in the logging (runs using `Robocorp Code`
  will automatically set it and show the details in the `ROBO TASKS OUTPUT` view).

## 2.0.0

### Backward incompatible changes:

By default all the libraries are now logged (so, now rules should be
added to opt-out of the logging instead of opting in to the logging).

To opt-out edit the `pyproject.toml` excluding what should not be logged.

i.e.:

```
[tool.robocorp.log]

log_filter_rules = [
    # Opt-out to the libraries which should not be logged.
    {name = "email", kind = "exclude"},
    {name = "urllib", kind = "exclude"},
]
```

It's possible to revert to the old behaviour (to opt-in selecting the
libraries to be logged by configuring the `default_library_filter_kind`
in `pyproject.toml`.

i.e.:

```
[tool.robocorp.log]

log_filter_rules = [
    # Opt-in to the libraries to be logged.
    {name = "RPA", kind = "log_on_project_call"},
]

default_library_filter_kind = "exclude"
```

## 1.0.0

- When collecting tasks properly flush `sys.stdout` prior to exiting process.
- Semantic versioning now followed.

## 0.4.1

- Updated `robocorp-log` to `0.3.1`.

## 0.4.0

- Updated `robocorp-log` to `0.3.0`.
- During task teardown a process snapshot is now included.
- After all tasks are run, if the process doesn't exit in 40 seconds
  (or the value specified in the `RC_DUMP_THREADS_AFTER_RUN_TIMEOUT`
  environment variable), the stack of the running threads are printed 
  to stderr. 

## 0.3.0

- Updated `robocorp-log` to `0.2.0`.

## 0.2.1

- Added py.typed marker file.
- Documentation updates

## 0.2.0

- New argument: `--no-status-rc`:
    When set, if running tasks has an error inside the task the return code of the process is 0 (
    if unsed the return code if an error is thrown inside a task the return code is 1).
- When collecting tasks redirect sys.stdout to sys.stderr so that only the expected json is outputed.
- Allow running multiple tasks.
- New decorator: `session_cache` allows a value to be cached until the task run session finishes.
- New decorator: `task_cache` allows a value to be cached until the current task run finishes.
- New API: `get_output_dir` provides the configured output directory.
- New API: `get_current_task` provides the task being currently run.

## 0.1.7

- Provide output in the console showing that a task is being run and the result of the run.
- Redirecting messages written to the console to log messages.
    The `--console-colors` arguments can be set to `auto` (where it'll decide the best approach to print with colors), `plain` to disable the colors or `ansi` to force colors to be printed with ansi chars.
- It's possible to setup the messages redirection by using either command line arguments (`--log-output-to-stdout=json`) or the `RC_LOG_OUTPUT_STDOUT=json` environment variable.
- Upgraded `robocorp-log` dependency to `0.0.15`. 

## 0.1.6

- Fixed case where the log would not be properly setup if `[tool.robocorp.log`] was not in `pyproject.toml`.
- Upgraded `robocorp-log` dependency to `0.0.13`. 

## 0.1.5

- First alpha release for `robocorp-tasks`.
- `@task` decorator to define entry points.
- Automatic logging 
    - Configures `robocorp-log` with reasonable defaults.
        - Rotate files after 5 files
        - Up to 1MB each
        - Log to `output`
        - Provide `output/log.html` when run finishes.
    - Log customization through `pyproject.toml`.
- Command line API which allows listing tasks with:
    - python -m robocorp.tasks list <directory>
- Command line API which allows running tasks with:
    - python -m robocorp.tasks run <directory> -t <task_name>
