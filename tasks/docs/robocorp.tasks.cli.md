<!-- markdownlint-disable -->

<a href="tasks\src\robocorp\tasks\cli.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.tasks.cli`
Main entry point for running tasks from robocorp-tasks. 

Note that it's usually preferable to use `robocorp-tasks` as a command line tool, using it programmatically through the main(args) in this module is also possible. 

Note: when running tasks, clients using this approach MUST make sure that any code which must be automatically logged is not imported prior the the `cli.main` call. 


---

<a href="tasks\src\robocorp\tasks\cli.py#L20"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `main`

```python
main(args=None, exit: bool = True) → int
```

Entry point for running tasks from robocorp-tasks. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
