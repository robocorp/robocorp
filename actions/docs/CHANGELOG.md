# Changelog

## 0.0.6 - 2024-01-18

- Provides support for calling `main` multiple times.
    - Modules containing `@action` are no longer reimported anymore.
    - Any `@action` that was already imported is still available for running in a new `main` call.
    - `RC_TASKS_SKIP_SESSION_SETUP` env variable may be used to skip setup of new `@setup`s found.
    - `RC_TASKS_SKIP_SESSION_TEARDOWN` env variable may be used to skip teardon of `@teardown`s found.

## 0.0.5 - 2024-01-14

- Fix main README and update docs.

## 0.0.4 - 2024-01-09

- Arguments to `@action` may be passed in a json file (with `--json-input=<path to .json file>`).
- Requires `robocorp-tasks >= 2.8.0` now.

## 0.0.3 - 2024-01-05

- Pass `@action(is_consequential=True)` to add `x-openai-isConsequential` option to action openapi spec (when used with the action-server).

## 0.0.2 - 2023-12-13

- Properly depend on `robocorp-tasks` version `2.6.0`.

## 0.0.1 - 2023-11-29

It's possible to define an action such as:

```python
from robocorp.actions import action

@action
def convert_to_int(value: str) -> int:
    return int(value)
```

And call it as:

```python
python -m robocorp.action -- --value=2
```
