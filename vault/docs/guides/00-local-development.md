# Local development

## Connecting to Control Room

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

## Using mock Vault

An alternative to using Vault from Control Room is to use a local file
with mock secrets. This enables development of a Robot without any existing
Control Room workspace.

**Note:** Secrets stored in a file are not safe to use with sensitive values,
and should only be used during development-time

File-based secrets can be set by defining two environment variables.

- ``RC_VAULT_SECRET_MANAGER``: `FileSecrets`
- ``RC_VAULT_SECRET_FILE``: Absolute path to the secrets database file

Example content of local secrets file as JSON:

```json
{
    "swaglabs": {
        "username": "standard_user",
        "password": "secret_sauce"
    }
}
```

Example as YAML:

```yaml

swaglabs:
    username: standard_user
    password: secret_sauce
```
