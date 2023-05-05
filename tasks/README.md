# robocorp-tasks

`robocorp-tasks` is a Python framework designed to simplify the development 
of Python automations.

> Note: The current version is still alpha but its public API is already meant
> to be stable and new releases should keep backward compatibility.

## Why

While Python is widely used in the automation world, many solutions end up being 
ad-hoc, making it difficult to navigate different projects and keep up with the
features required for analysing the results of such automations afterwards.

## How

`robocorp-tasks` provides a runner for running tasks that offers logging 
out of the box for Python code (showing method calls, arguments, assigns, etc)
by leveraging `robocorp-log`, and managing the lifecycle for running such tasks.
 
### Installation

To install `robocorp-tasks`, use the following command:

`pip install robocorp-tasks`


## Usage

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


## Auto logging customization


Following the initial steps outlined above should be sufficient to get comprehensive 
logging for all user code executed. However, note that it won't log calls from 
libraries by default, as it may be difficult to separate the libraries that are 
important for a project from those that are just noise.

To add custom logging for libraries like `rpaframework`, `Selenium` and others, create a 
`pyproject.toml` file and place it in the root of your project. 
Then, customize the `[tool.robocorp.log]` section to add `log_filter_rules`.


`log_filter_rules` is a list of dictionaries where entries may be added to specify
how to handle logging for a particular module.

There are three different logging configurations that may be applied:

- `exclude` (default for library code): skips logging a module.
- `full_log` (default for user code): logs a module with full information, such as method calls, arguments, yields, local assigns, and more.
- `log_on_project_call` logs only method calls, arguments, return values and exceptions, but only when a library method is called from user code. This configuration is meant to be used for library logging.

Example of `pyproject.toml` where the `rpaframework` and `selenium` 
libraries are configured to be logged:


```
[tool.robocorp.log]

log_filter_rules = [
    {name = "RPA", kind = "log_on_project_call"},
    {name = "selenium", kind = "log_on_project_call"},
    {name = "SeleniumLibrary", kind = "log_on_project_call"},
]
```

Note that when specifying a module name to match in `log_filter_rules`, 
the name may either match exactly or the module name must start with the 
name followed by a dot.

This means that, for example, `RPA` would match `RPA.Browser`,
but not `RPAmodule` nor `another.RPA`.


## Log output customization

By default, the log output will be saved to an `output` directory, where each file 
can be up to `1MB` and up to `5` files are kept before old ones are deleted. 
When the run finishes, a `log.html` file will be created in the output directory 
containing the log viewer with the log contents embedded.

However, you can customize the log output by changing the output directory, 
maximum number of log files to keep, and maximum size of each output file. 
You can do this through the command line by passing the appropriate arguments 
when running `python -m robocorp.tasks run`.

For example, to change the output directory to `my_output`, run:

```
python -m robocorp.tasks run path/to/tasks.py -o my_output
```

You can also set the maximum number of output files to keep by passing 
`--max-log-files` followed by a number. For example, to keep up to `10` log files, run:


```
python -m robocorp.tasks run path/to/tasks.py --max-log-files 10
```

Finally, you can set the maximum size of each output file by passing 
`--max-log-file-size` followed by a size in megabytes (e.g.: `2MB` or `1000kb`).

For example, to set the maximum size of each output file to `500kb`, run:


```
python -m robocorp.tasks run path/to/tasks.py --max-log-file-size 500kb
```

## License: Apache 2.0
## Copyright: Robocorp Technologies, Inc.

