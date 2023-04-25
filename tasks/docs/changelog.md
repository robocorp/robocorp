0.1.5
-----------------------------

- First alpha release for `robocorp-tasks`.
- `@task` decorator to define entry points.
- Automatic logging 
    - Configures `robocorp-log` with reasonable defaults.
        - Rotate files after 5 files
        - Up to 1MB each
        - Log to `output`
        - Provide `output/log.html` when run finishes.
    - Log customization through `pyproject.toml`.
- Command line API which allows listing tasks with:
    - python -m robocorp.tasks list <directory>
- Command line API which allows running tasks with:
    - python -m robocorp.tasks run <directory> -t <task_name>