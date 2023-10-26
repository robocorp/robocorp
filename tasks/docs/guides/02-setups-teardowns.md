# Setups and teardowns

The library contains two fixture methods, `setup` and `teardown`, that can be
used to call arbitrary functions before and after tasks are run.

The fixtures receive as arguments the tasks objects that the library has parsed
from the tasks file, which allows fixtures to behave differently based on which
task is going to be executed or if task failed or passed.

This is useful for having shared initialization or clean-up steps for all tasks,
or for ensuring that a function is always executed when implementing libraries.

## Scopes

The fixtures can be optionally configured with a `scope` that determines if a
fixture is run once before or after all tasks, or each time a task will execute.
Valid values are `task` and `session`.

For `task` scopes (default), the argument is the single task that will or was run.
For `session` scopes, the argument to the fixture is a list of tasks.

## Task objects

A `Task` object is the internal representation of a parsed task in a Python file.
It contains, for instance, the `filename` and `lineno` of the function, but
also the `status` and optional `message` after it has been executed.

## Example usage

```python
from robocorp import browser
from robocorp.tasks import task, teardown


@setup(scope="session")
def configure_browser(tasks):
    browser.configure(headless=True, screenshot="only-on-failure")


@teardown
def handle_error(task):
    if task.failed:
        print(f"Task '{task.name}' failed: {task.message}")


@task
def scrape_website():
    ...


@task
def process_data():
    ...
```

## Yielding fixtures

Sometimes it's necessary to access a resource created in a `setup` inside a
`teardown` fixture. In these cases, it's possible to create a `setup` fixture
that `yield`s.

The library will call the fixture up until the `yield` statement, execute the task,
and then call the rest of the fixture (in reverse order):

```python
import time
from robocorp.tasks import setup


@setup
def measure_time(task):
    start = time.time()
    yield  # Task executes here
    duration = time.time() - start
    print(f"Task {task.name} took {duration} seconds")


@task
def my_long_task():
    ...
```
