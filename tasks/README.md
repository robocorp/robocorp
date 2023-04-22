# Robocorp Tasks

Robocorp Tasks is a python framework to ease RPA development in Python.


Concepts:

`Robocorp Tasks` expects tasks to be run to be marked as decorators in Python.


```
from robocorp.tasks import task

@task
def my_task():
    ...
    
```

## Command line API:

### Run tasks using the command line:

```
python -m robocorp.tasks run <directory> -t <task_name>
```


### List available tasks

```
python -m robocorp.tasks list <directory>
```
