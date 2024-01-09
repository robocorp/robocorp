
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
def convert_to_int(value:str) -> int:
    return int(value)
```

And call it as:

```python
python -m robocorp.action -- --value=2
```