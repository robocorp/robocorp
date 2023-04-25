"""
robocorp-tasks: mark entry points with:

```
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
  
  
Note: Using the `cli.main(args)` is possible to run tasks programmatically, but
clients using this approach MUST make sure that any code which must be
automatically logged is not imported prior the the `cli.main` call.
"""

from ._decorators import task

__version__ = "0.1.4"
version_info = [int(x) for x in __version__.split(".")]
