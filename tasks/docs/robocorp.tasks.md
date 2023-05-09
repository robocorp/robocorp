<!-- markdownlint-disable -->

<a href="..\..\tasks\robocorp\tasks#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.tasks`
Robocorp tasks helps in creating entry points for your automation project. 

To use: 

Mark entry points with: 

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

 

Note: Using the `cli.main(args)` is possible to run tasks programmatically, but clients using this approach MUST make sure that any code which must be automatically logged is not imported prior the the `cli.main` call. 

**Global Variables**
---------------
- **version_info**

---

<a href="..\..\tasks\robocorp\tasks\task#L42"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `task`

```python
task(func)
```

Decorator for tasks (entry points) which can be executed by `robocorp.tasks`. 

i.e.: 

If a file such as tasks.py has the contents below: 

..  from robocorp.tasks import task 

 @task  def enter_user():  ... 



It'll be executable by robocorp tasks as: 

python -m robocorp.tasks run tasks.py -t enter_user 



**Args:**
 
 - <b>`func`</b>:  A function which is a task to `robocorp.tasks`. 


---

<a href="..\..\tasks\robocorp\tasks\session_cache#L73"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `session_cache`

```python
session_cache(func)
```

Provides decorator which caches return and clears automatically when all tasks have been run. 

A decorator which automatically cache the result of the given function and will return it on any new invocation until robocorp-tasks finishes running all tasks. 

The function may be either a generator with a single yield (so, the first yielded value will be returned and when the cache is released the generator will be resumed) or a function returning some value. 



**Args:**
 
 - <b>`func`</b>:  wrapped function. 


---

<a href="..\..\tasks\robocorp\tasks\task_cache#L94"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `task_cache`

```python
task_cache(func)
```

Provides decorator which caches return and clears it automatically when the current task has been run. 

A decorator which automatically cache the result of the given function and will return it on any new invocation until robocorp-tasks finishes running the current task. 

The function may be either a generator with a single yield (so, the first yielded value will be returned and when the cache is released the generator will be resumed) or a function returning some value. 



**Args:**
 
 - <b>`func`</b>:  wrapped function. 


---

<a href="..\..\tasks\robocorp\tasks\get_output_dir#L115"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_output_dir`

```python
get_output_dir() → Optional[Path]
```

Provide the output directory being used for the run or None if there's no output dir configured. 


---

<a href="..\..\tasks\robocorp\tasks\get_current_task#L127"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_current_task`

```python
get_current_task() → Optional[ITask]
```

Provides the task which is being currently run or None if not currently running a task. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
