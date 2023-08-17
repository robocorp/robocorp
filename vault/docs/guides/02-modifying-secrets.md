# Modifying secrets

Secrets in Vault can be modified during Robot executions, which can be useful
for updating ephemeral values such as authentication tokens.

## Creating

New secrets be created with the `create_secret` function:

```python
import secrets

from robocorp.tasks import task
from robocorp import vault

@task
def create_secret():
    vault.create_secret(
        name="generated_token",
        description="This secret was created by an automation",
        values={
            "username": "bot@example.com",
            "token": secrets.token_urlsafe(16),
        }
    )
```

## Updating

The functions `create_secret` and `get_secret` return a container of
secret values, which can be modified and updated back to Vault:

```python
import secrets

from robocorp.tasks import task
from robocorp import vault

@task
def update_secret():
    secret = vault.get_secret("generated_token")
    secret["token"] = secrets.token_urlsafe(16)
    vault.set_secret(secret)
```
