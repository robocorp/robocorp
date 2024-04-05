## Getting secrets in Actions

Starting with `robocorp-actions 0.2.0`, it's possible to receive
secrets as arguments in the `@action`.

The requisite for that is adding an argument and typing it with the `Secret` type.

### Example:

```
from robocorp.actions import action, Secret

@action
def my_action(my_secret: Secret):
    login(secret.value)

```

When developing, it's possible to specify the secret directly in the json input as a string.
