# Changelog

## Unreleased

## 0.2.0 - 2024-04-10

- `python -m robocorp.actions list` now has information on the managed parameters
  (`managed_params_schema`, which is a dict from parameter name to parameter
   information is given for each task).
- Parameters in `@action` typed as `robocorp.actions.Secret` will now be considered
  managed parameters (the client must to provide the secret information when
  running the action).
- Update **robocorp-tasks** dependency to `3.1.0`.

## 0.1.3 - 2024-04-09

- Update **robocorp-tasks** dependency to `3.0.3`.

## 0.1.2 - 2024-04-08

- Alignment with **robocorp-tasks** `3.0.2`.

## 0.1.1 - 2024-04-08

- Update package's main README.

## 0.1.0 - 2024-03-15

- `request: Request` is now a managed parameter when using `robocorp-actions`. Note
  that by default it'll be empty, but when called from the `Action Server`, it'll
  have `headers` and `cookies` available.

## 0.0.9 - 2024-03-13

- References in the schema are resolved (so, the schema for a field is valid when embedded inside a larger schema).

## 0.0.8 - 2024-03-11

- `pydantic` models are accepted as the input and output of `@action`s. 

## 0.0.7 - 2024-01-31

- When actions are imported they're also automatically linted for the following errors:
    - Mising docstrings (error)
    - Mising docstrings docstring (error)
    - Return statement is found (error).
    - Each argument has a description in the docstring (error).
    - Arguments are properly typed (warning).
    - Return is properly typed (warning).
- Files named `*task*.py` are no longer loaded by default in actions.

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
