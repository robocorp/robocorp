# robocorp-tasks

`robocorp-tasks` is a Python framework designed to simplify the development 
of Python automations.

> Note: The current version (2.0.0) is now in beta. Semantic versioning is used in the project.

## Why

While Python is widely used in the automation world, many solutions end up being 
ad-hoc, making it difficult to navigate different projects and keep up with the
features required for analysing the results of such automations afterwards.

## How

`robocorp-tasks` provides a runner for running tasks that offers logging 
out of the box for Python code (showing method calls, arguments, assigns, etc)
by leveraging `robocorp-log`, and managing the lifecycle for running such tasks.

## Getting started

Replace the code in your `__main__` with a method that has the name of your task
(which should not have parameters) and decorate it with the `@task` decorator, like this:

i.e.:


```
from robocorp.tasks import task

@task
def my_task():
    ...
    
```

2. Call your task using the command line below, customizing the directory and task name as needed:


```
python -m robocorp.tasks run <path/to/file.py or directory> -t <task_name>
```

Note: if you have only one defined task in your target, the `-t <task_name>` option is not needed. 

Note: the task name is the name of the method decorated with `@task`.

Note: if a directory is given, only files named `*task*.py` will be used for collection.

Note: in the current version only one task can be run per invocation. If more than one task 
is found an error will be given and no tasks will be run.

3. View the log results in `output/log.html`.

## Guides

- [Logging customization](https://github.com/robocorp/robo/blob/master/tasks/docs/guides/00-logging-customization.md)
- [Output customization](https://github.com/robocorp/robo/blob/master/tasks/docs/guides/01-output-customization.md)

## API Reference

Information on specific functions or classes: [robocorp.tasks](https://github.com/robocorp/robo/blob/master/tasks/docs/api/robocorp.tasks.md)

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robo/blob/master/tasks/docs/CHANGELOG.md).
