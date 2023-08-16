<!-- markdownlint-disable -->

# module `robocorp.tasks`
**Source:** [`__init__.py:0`](https://github.com/robocorp/robo/tree/master/tasks/src/robocorp/tasks/__init__.py#L0)
Robocorp tasks helps in creating entry points for your automation project.

To use:

Mark entry points with:

```
from robocorp.tasks import task

@task
def my_method():
    ...
```

Running options:

Runs all the tasks in a .py file:

`python -m robocorp.tasks run <path_to_file>`

Run all the tasks in files named *task*.py:

`python -m robocorp.tasks run <directory>`

Run only tasks with a given name:

`python -m robocorp.tasks run <directory or file> -t <task_name>`



Note: Using the `cli.main(args)` is possible to run tasks programmatically, but clients using this approach MUST make sure that any code which must be automatically logged is not imported prior the the `cli.main` call.


---

## function `task`
**Source:** [`__init__.py:43`](https://github.com/robocorp/robo/tree/master/tasks/src/robocorp/tasks/__init__.py#L43)

```python
task(func)
```

Decorator for tasks (entry points) which can be executed by `robocorp.tasks`.

i.e.:

If a file such as tasks.py has the contents below:

.. from robocorp.tasks import task

@taskdef enter_user():...



It'll be executable by robocorp tasks as:

python -m robocorp.tasks run tasks.py -t enter_user



**Args:**

 - <b>`func`</b>:  A function which is a task to `robocorp.tasks`.


---

## function `session_cache`
**Source:** [`__init__.py:74`](https://github.com/robocorp/robo/tree/master/tasks/src/robocorp/tasks/__init__.py#L74)

```python
session_cache(func)
```

Provides decorator which caches return and clears automatically when all tasks have been run.

A decorator which automatically cache the result of the given function and will return it on any new invocation until robocorp-tasks finishes running all tasks.

The function may be either a generator with a single yield (so, the first yielded value will be returned and when the cache is released the generator will be resumed) or a function returning some value.



**Args:**

 - <b>`func`</b>:  wrapped function.


---

## function `task_cache`
**Source:** [`__init__.py:96`](https://github.com/robocorp/robo/tree/master/tasks/src/robocorp/tasks/__init__.py#L96)

```python
task_cache(func)
```

Provides decorator which caches return and clears it automatically when the current task has been run.

A decorator which automatically cache the result of the given function and will return it on any new invocation until robocorp-tasks finishes running the current task.

The function may be either a generator with a single yield (so, the first yielded value will be returned and when the cache is released the generator will be resumed) or a function returning some value.



**Args:**

 - <b>`func`</b>:  wrapped function.


---

## function `get_output_dir`
**Source:** [`__init__.py:118`](https://github.com/robocorp/robo/tree/master/tasks/src/robocorp/tasks/__init__.py#L118)

```python
get_output_dir() → Optional[Path]
```

Provide the output directory being used for the run or None if there's no output dir configured.


---

## function `get_current_task`
**Source:** [`__init__.py:131`](https://github.com/robocorp/robo/tree/master/tasks/src/robocorp/tasks/__init__.py#L131)

```python
get_current_task() → Optional[ITask]
```

Provides the task which is being currently run or None if not currently running a task.


