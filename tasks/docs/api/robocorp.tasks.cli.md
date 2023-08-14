<!-- markdownlint-disable -->

# module `robocorp.tasks.cli` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/tasks/src/robocorp/tasks/cli.py#L0)

Main entry point for running tasks from robocorp-tasks.

Note that it's usually preferable to use `robocorp-tasks` as a command line tool, using it programmatically through the main(args) in this module is also possible.

Note: when running tasks, clients using this approach MUST make sure that any code which must be automatically logged is not imported prior the the `cli.main` call.


---

## function `main` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/tasks/src/robocorp/tasks/cli.py#L19)


```python
main(args=None, exit: bool = True) → int
```

Entry point for running tasks from robocorp-tasks.


