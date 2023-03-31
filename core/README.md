# Robo

Robo is a python framework to ease RPA development in Python.


Concepts:

`Robo` expects tasks to be run to be marked as decorators in Python.


```
from robo import task

@task
def my_task():
    ...
    
```

## Command line API:

### Run tasks using the command line:

```
python -m robo run <directory> -t <task_name>
```


### List available tasks

```
python -m robo list <directory>
```
