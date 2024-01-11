# Using Robocorp libraries in existing projects

It's possible to use certain features - such as logging - from the `robo` framework in existing [rcc](https://github.com/robocorp/rcc) projects. It can be done by adding a single `pip` dependency and making a few simple changes.

> Note: The current version is still alpha but its public API is already meant to be stable and new releases should keep backward compatibility.

## Example project

In our simple example project we have `rcc`'s required `robot.yaml` and `conda.yaml`, and a simple Python script:

`robot.yaml`
```yaml
tasks:
  Run Task:
    shell: python task.py

environmentConfigs:
  - conda.yaml
artifactsDir: output
PATH:
  - .
PYTHONPATH:
  - .
ignoreFiles:
  - .gitignore
```

`conda.yaml`
```yaml
channels:
  - conda-forge

dependencies:
  - python=3.9.13
  - pip=22.1.2
  - pip:
      - rpaframework==22.5.3
```

`task.py`
```python
def hello_world():
    print("Hello world!")

if __name__ == "__main__":
    hello_world()
```

## Adding the dependency

The recommended way to use the integrated logging is through the library `robocorp-tasks`. This is the core library of the framework that handles the initialization and life-cycle of tasks. It also brings in the logging package, `robocorp-log`.

In the existing `conda.yaml`, add a dependency for the `tasks` library:

```yaml
channels:
  - conda-forge
dependencies:
  - python=3.9.13
  - pip=22.1.2
  - pip:
      - rpaframework==22.5.3
      - robocorp-tasks==0.3.0
```
## Defining a task

Using the library happens with the `@task` decorator:

```python
from robocorp.tasks import task

@task
def hello_world():
    print("Hello world!")
```

This tells the framework that the decorated function is a runnable task. As you can notice, the old code for checking `__main__` can now be removed.

## Modifying the shell command

To run a task, the library exposes a script that can be called from the command line:

`python -m robocorp.tasks run task.py`

If the file has multiple `@task` definitions, the name of the function can be given as an argument:

`python -m robocorp.tasks run task.py -t hello_world`

This command can be subsituted in the existing `robot.yaml`:

```yaml
tasks:
  Run Task:
    shell: python -m robocorp.tasks run task.py
environmentConfigs:
  - conda.yaml
artifactsDir: output
PATH:
  - .
PYTHONPATH:
  - .
ignoreFiles:
  - .gitignore
```

## Using and configuring logging

After running, the generated log can be found from `output/log.html`. This is a detailed HTML log of the Python execution.

While the default configuration should be good enough to get started, sometimes it's necessary to suppress certain libraries, or add more logging while debugging.

The configuration of the library happens through the Python-standard `pyproject.toml`, within the section `tool.robocorp.log`:
```
[tool.robocorp.log]

log_filter_rules = [
    {name = "MyCoolLibrary", kind = "full_log"},
    {name = "passwd", kind = "exclude"}
]
```

To see more documentation for configuration, see the [README.md](https://github.com/robocorp/robocorp/blob/master/log/README.md) of the library.
