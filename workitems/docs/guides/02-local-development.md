# Local development

## Using the VSCode extension

If you are developing in VSCode with the [Robocorp Code extension](https://robocorp.com/docs/setup/development-environment#visual-studio-code-with-robocorp-extensions),
you can utilize the built in local development features described in the
[Developing with work items locally](https://robocorp.com/docs/development-guide/control-room/work-items#developing-with-work-items-locally)
section of the [Using work items](https://robocorp.com/docs/development-guide/control-room/work-items)
development guide.

This allows you to develop and test your work items before deploying
to Control Room.

## Using a custom editor

It's also possible to develop locally with a custom editor, but it requires
some configuration.

To enable the development mode for the library, you should set the environment
variable `RC_WORKITEM_ADAPTER`. The value can be a fully qualified class name
or one of the built-in aliases:

- `file` (default) – local JSON files for simulating queues (accepts
    `FileAdapter` for backwards compatibility).
- `sqlite` – SQLite-backed queue. Provide `RC_WORKITEM_DB_PATH` and optional
    `RC_WORKITEM_QUEUE_NAME`. No extra dependencies required.
- `redis` – Redis-backed queue. Install with `pip install "robocorp-workitems[redis]"`
    and set Redis connection variables such as `REDIS_HOST`.
- `docdb` – MongoDB/DocumentDB-backed queue. Install with
    `pip install "robocorp-workitems[docdb]"` and set the relevant `DOCDB_*`
    environment variables.

The `file` adapter continues to rely on JSON files. When using it, set the
environment variables `RC_WORKITEM_INPUT_PATH` and `RC_WORKITEM_OUTPUT_PATH`,
which should contain the paths to the input and output JSON files. The output
file will be created by the library, but the input file should be created
manually.


An example of an input file with one work item:

```json
[
    {
        "payload": {
            "variable1": "a-string-value",
            "variable2": ["a", "list", "value"]
        },
        "files": {
            "file1": "path/to/file.ext"
        }
    }
]
```

The format of the file is a list of objects, where each item in the list
corresponds to one work item. The `payload` key can contain any arbitrary JSON,
and the `files` key is pairs of names and paths to files.
