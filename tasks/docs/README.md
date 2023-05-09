<!-- markdownlint-disable -->

# API Overview

## Modules

- [`robocorp.tasks`](./robocorp.tasks.md#module-robocorptasks): Robocorp tasks helps in creating entry points for your automation project.
- [`robocorp.tasks.cli`](./robocorp.tasks.cli.md#module-robocorptaskscli): Main entry point for running tasks from robocorp-tasks.

## Classes

- No classes

## Functions

- [`tasks.get_current_task`](./robocorp.tasks.md#function-get_current_task): Provides the task which is being currently run or None if not currently running a task.
- [`tasks.get_output_dir`](./robocorp.tasks.md#function-get_output_dir): Provide the output directory being used for the run or None if there's no output dir configured.
- [`tasks.session_cache`](./robocorp.tasks.md#function-session_cache): Provides decorator which caches return and clears automatically when all tasks have been run.
- [`tasks.task`](./robocorp.tasks.md#function-task): Decorator for tasks (entry points) which can be executed by `robocorp.tasks`.
- [`tasks.task_cache`](./robocorp.tasks.md#function-task_cache): Provides decorator which caches return and clears it automatically when the current task has been run.
- [`cli.main`](./robocorp.tasks.cli.md#function-main): Entry point for running tasks from robocorp-tasks.


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
