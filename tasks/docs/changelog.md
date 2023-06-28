2.0.0
-----------------------------

Backward incompatible changes:

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


1.0.0
-----------------------------

- When collecting tasks properly flush `sys.stdout` prior to exiting process.
- Semantic versioning now followed.

0.4.1
-----------------------------

- Updated `robocorp-log` to `0.3.1`.

0.4.0
-----------------------------

- Updated `robocorp-log` to `0.3.0`.
- During task teardown a process snapshot is now included.
- After all tasks are run, if the process doesn't exit in 40 seconds
  (or the value specified in the `RC_DUMP_THREADS_AFTER_RUN_TIMEOUT`
  environment variable), the stack of the running threads are printed 
  to stderr. 

0.3.0
-----------------------------

- Updated `robocorp-log` to `0.2.0`.


0.2.1
-----------------------------

- Added py.typed marker file.
- Documentation updates


0.2.0
-----------------------------

- New argument: `--no-status-rc`:
    When set, if running tasks has an error inside the task the return code of the process is 0 (
    if unsed the return code if an error is thrown inside a task the return code is 1).
- When collecting tasks redirect sys.stdout to sys.stderr so that only the expected json is outputed.
- Allow running multiple tasks.
- New decorator: `session_cache` allows a value to be cached until the task run session finishes.
- New decorator: `task_cache` allows a value to be cached until the current task run finishes.
- New API: `get_output_dir` provides the configured output directory.
- New API: `get_current_task` provides the task being currently run.

0.1.7
-----------------------------

- Provide output in the console showing that a task is being run and the result of the run.
- Redirecting messages written to the console to log messages.
    The `--console-colors` arguments can be set to `auto` (where it'll decide the best approach to print with colors), `plain` to disable the colors or `ansi` to force colors to be printed with ansi chars.
- It's possible to setup the messages redirection by using either command line arguments (`--log-output-to-stdout=json`) or the `RC_LOG_OUTPUT_STDOUT=json` environment variable.
- Upgraded `robocorp-log` dependency to `0.0.15`. 


0.1.6
-----------------------------

- Fixed case where the log would not be properly setup if `[tool.robocorp.log`] was not in `pyproject.toml`.
- Upgraded `robocorp-log` dependency to `0.0.13`. 

0.1.5
-----------------------------

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