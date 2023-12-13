
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