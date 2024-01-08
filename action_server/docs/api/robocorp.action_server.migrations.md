<!-- markdownlint-disable -->

# module `robocorp.action_server.migrations`

**Source:** [`__init__.py:0`](https://github.com/robocorp/robo/tree/master/action_server/src/robocorp/action_server/migrations/__init__.py#L0)

The way that migrations work is the following:

We have a table with the id and name of each migration applied.

When starting up we connect to the db and see the current version. Then, we apply each pending migration since the last version.

## Variables

- **MIGRATION_ID_TO_NAME**
- **CURRENT_VERSION**

______________________________________________________________________

## function `migrate_db`

**Source:** [`__init__.py:48`](https://github.com/robocorp/robo/tree/master/action_server/src/robocorp/action_server/migrations/__init__.py#L48)

```python
migrate_db(
    db_path: Union[Path, str],
    to_version=3,
    database: Optional[ForwardRef('Database')] = None
) → bool
```

Returns true if the migration worked properly or if the migration was not needed and false if the migration could not be done for some reason.

:param database: Expected to be passed when dealing with an in-memory database.

______________________________________________________________________

## function `db_migration_pending`

**Source:** [`__init__.py:133`](https://github.com/robocorp/robo/tree/master/action_server/src/robocorp/action_server/migrations/__init__.py#L133)

```python
db_migration_pending(db_path: Union[Path, str]) → bool
```

______________________________________________________________________

## class `Migration`

**Source:** [`__init__.py:34`](https://github.com/robocorp/robo/tree/master/action_server/src/robocorp/action_server/migrations/__init__.py#L34)

Migration(id: int, name: str)

### method `__init__`

```python
__init__(id: int, name: str) → None
```
