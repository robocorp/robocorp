<!-- markdownlint-disable -->

# module `robocorp.tasks`

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

# Functions

______________________________________________________________________

## `task`

Decorator for tasks (entry points) which can be executed by `robocorp.tasks`.

i.e.:

If a file such as tasks.py has the contents below:

```python
from robocorp.tasks import task

@task
def enter_user():
    ...
```

It's also possible to pass options to the task decorator that can then be introspected by `task.options`:

```python
from robocorp.tasks import task

@task(this_is_option="option")
def enter_user():
    ...
```

It'll be executable by robocorp tasks as:

python -m robocorp.tasks run tasks.py -t enter_user

**Args:**

- <b>`func`</b>:  A function which is a task to `robocorp.tasks`.
- <b>`**kwargs`</b>:  Options to be introspected by `task.options`.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/__init__.py#L45)

```python
task(*args, **kwargs)
```

______________________________________________________________________

## `setup`

Run code before any tasks start, or before each separate task.

Receives as an argument the task or tasks that will be run.

Can be used as a decorator without arguments:

```python
from robocorp.tasks import setup

@setup
def my_fixture(task):
    print(f"Before task: {task.name}")
```

Alternatively, can be called with a `scope` argument to decide when the fixture is run:

```python
from robocorp.tasks import setup

@setup(scope="task")
def before_each(task):
    print(f"Running task '{task.name}'")

@setup(scope="session")
def before_all(tasks):
    print(f"Running {len(tasks)} task(s)")
```

By default, runs setups in `task` scope.

The `setup` fixture also allows running code after the execution, if it `yield`s the execution to the task(s):

```python
import time
from robocorp.tasks import setup

@setup
def measure_time(task):
    start = time.time()
    yield  # Task executes here
    duration = time.time() - start
    print(f"Task took {duration} seconds")

@task
def my_long_task():
    ...
```

**Note:** If fixtures are defined in another file, they need to be imported in the main tasks file to be taken into use

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/_fixtures.py#L26)

```python
setup(
    *args,
    **kwargs
) → Union[Callable[[ITask], Any], Callable[[Callable[[ITask], Any]], Callable[[ITask], Any]], Callable[[Callable[[Sequence[ITask]], Any]], Callable[[Sequence[ITask]], Any]]]
```

______________________________________________________________________

## `teardown`

Run code after tasks have been run, or after each separate task.

Receives as an argument the task or tasks that were executed, which contain (among other things) the resulting status and possible error message.

Can be used as a decorator without arguments:

```python
from robocorp.tasks import teardown

@teardown
def my_fixture(task):
    print(f"After task: {task.name})
```

Alternatively, can be called with a `scope` argument to decide when the fixture is run:

```python
from robocorp.tasks import teardown

@teardown(scope="task")
def after_each(task):
    print(f"Task '{task.name}' status is '{task.status}'")

@teardown(scope="session")
def after_all(tasks):
    print(f"Executed {len(tasks)} task(s)")
```

By default, runs teardowns in `task` scope.

**Note:** If fixtures are defined in another file, they need to be imported in the main tasks file to be taken into use

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/_fixtures.py#L148)

```python
teardown(
    *args,
    **kwargs
) → Union[Callable[[ITask], Any], Callable[[Callable[[ITask], Any]], Callable[[ITask], Any]], Callable[[Callable[[Sequence[ITask]], Any]], Callable[[Sequence[ITask]], Any]]]
```

______________________________________________________________________

## `session_cache`

Provides decorator which caches return and clears automatically when all tasks have been run.

A decorator which automatically cache the result of the given function and will return it on any new invocation until robocorp-tasks finishes running all tasks.

The function may be either a generator with a single yield (so, the first yielded value will be returned and when the cache is released the generator will be resumed) or a function returning some value.

**Args:**

- <b>`func`</b>:  wrapped function.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/__init__.py#L98)

```python
session_cache(func)
```

______________________________________________________________________

## `task_cache`

Provides decorator which caches return and clears it automatically when the current task has been run.

A decorator which automatically cache the result of the given function and will return it on any new invocation until robocorp-tasks finishes running the current task.

The function may be either a generator with a single yield (so, the first yielded value will be returned and when the cache is released the generator will be resumed) or a function returning some value.

**Args:**

- <b>`func`</b>:  wrapped function.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/__init__.py#L120)

```python
task_cache(func)
```

______________________________________________________________________

## `get_output_dir`

Provide the output directory being used for the run or None if there's no output dir configured.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/__init__.py#L142)

```python
get_output_dir() → Optional[Path]
```

______________________________________________________________________

## `get_current_task`

Provides the task which is being currently run or None if not currently running a task.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/__init__.py#L155)

```python
get_current_task() → Optional[ITask]
```

______________________________________________________________________

# Class `ITask`

## Properties

- `failed`

Returns true if the task failed. (in which case usually exc_info is not None).

- `input_schema`

- `lineno`

- `name`

- `output_schema`

## Methods

______________________________________________________________________

### `run`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/tasks/src/robocorp/tasks/_protocols.py#L82)

```python
run() → Any
```

# Enums

______________________________________________________________________

## `Status`

Task state

### Values

- **NOT_RUN** = NOT_RUN
- **PASS** = PASS
- **FAIL** = FAIL
