# Robocorp Control Room Vault API library

`robocorp-vault` is a library that provides read and write access to the [Vault](https://robocorp.com/docs/development-guide/variables-and-secrets/vault)
in Robocorp Control Room, which can be used to store and retrieve secret values such as passwords.

## Usage

### Reading secrets

A secret consists of a name, an optional description, and a map of
keys and values. For instance, one secret can be login credentials for a website,
which includes both a username and a password:

```python
from robocorp.tasks import task
from robocorp import vault

@task
def inspect_secret():
    secret = vault.get_secret("login_credentials")
    print("Secret name:", secret.name)
    print("Secret description:", secret.description)
    print("Secret keys:", secret.keys())
    print("Secret value:", secret["username"])
```

### Creating secrets

Secrets can be also created and updated from within the execution:

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

### Updating secrets

Sometimes it's necessary to update parts of an existing secret:

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

## Hiding values

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

## Local development

### Connecting to Control Room

The usage of Vault relies on environment variables, which are normally set
automatically by the Robocorp Agent or Assistant when a run is executed via
Control Room.

When developing robots locally in VSCode, you can use the
[Robocorp Code Extension](https://robocorp.com/docs/developer-tools/visual-studio-code/extension-features#connecting-to-control-room-vault)
to set these variables automatically as well.

Alternatively, you may set these environment variables manually using
[rcc](https://robocorp.com/docs/rcc/workflow) or directly in some other fashion.
The specific variables which must exist are:

- ``RC_API_SECRET_HOST``: URL to Robocorp Vault API
- ``RC_API_SECRET_TOKEN``: API Token for Robocorp Vault API
- ``RC_WORKSPACE_ID``: Control Room Workspace ID

### Using mock Vault

An alternative to using Vault from Control Room is to use a local file
with mock secrets. This enables development of a Robot without any existing
Control Room workspace.

**Note:** Secrets stored in a file are not safe to use with sensitive values,
and should only be used during development-time

File-based secrets can be set by defining two environment variables.

- ``RC_VAULT_SECRET_MANAGER``: ``FileSecrets`
- ``RC_VAULT_SECRET_FILE``: Absolute path to the secrets database file

Example content of local secrets file:

```json
{
    "swaglabs": {
        "username": "standard_user",
        "password": "secret_sauce"
    }
}
```

OR

```yaml

swaglabs:
    username: standard_user
    password: secret_sauce
```
