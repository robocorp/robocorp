# Hiding values

Secret values (either received or sent) will be automatically hidden by the
library, if the library `robocorp.log` is available in the environment. It is
still imperative that any code that handles secret values does not expose
them by accident before interacting with Vault.

For example, when setting new values hide all variables already in the
enclosing scope:

```python
from robocorp.tasks import task
from robocorp import vault, log


@task
def sensitive_data():
    with log.suppress_variables():
        username, password = generate_credentials()
        vault.set_secret("credentials", {
            "username": username,
            "password": password,
        })
```
