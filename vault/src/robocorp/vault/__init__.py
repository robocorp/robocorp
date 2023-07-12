"""`robocorp.vault` is a library for interacting with secrets stored in the ``Robocorp Control Room Vault``.

Uses ``Robocorp Control Room Vault`` (by default) or file-based secrets, which can be taken
into use by setting some environment variables.

Robocorp Vault relies on environment variables, which are normally set
automatically by the Robocorp Work Agent or Assistant when a run is
initialized by the Robocorp Control Room. When developing robots locally
in VSCode, you can use the `Robocorp Code Extension`_ to set these
variables automatically as well.

Alternatively, you may set these environment variable manually using
`rcc`_ or directly in some other fashion. The specific variables which
must exist are:

- ``RC_API_SECRET_HOST``: URL to Robocorp Vault API
- ``RC_API_SECRET_TOKEN``: API Token for Robocorp Vault API
- ``RC_WORKSPACE_ID``: Control Room Workspace ID

.. _Robocorp Control Room Vault: https://robocorp.com/docs/development-guide/variables-and-secrets/vault
.. _Robocorp Code Extension: https://robocorp.com/docs/developer-tools/visual-studio-code/extension-features#connecting-to-control-room-vault
.. _rcc: https://robocorp.com/docs/rcc/workflow

File-based secrets can be set by defining two environment variables.

- ``RC_VAULT_SECRET_MANAGER``: FileSecrets
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

Example:

```python    
from robocorp import vault

def reading_secrets():
    secrets_container = vault.get_secret('swaglabs')
    print(f"My secrets: {secrets_container}")
    
def modifying_secrets():
    secret = vault.get_secret("swaglabs")
    secret["username"] = "nobody"
    vault.set_secret(secret)
```
"""  # noqa: E501


from contextlib import nullcontext
from functools import lru_cache

from ._secrets import SecretContainer

__version__ = "1.1.0"
version_info = [int(x) for x in __version__.split(".")]


@lru_cache
def _get_vault():
    from ._vault import Vault

    return Vault()


def get_secret(secret_name: str) -> SecretContainer:
    """Get secret defined with given name.

    Args:
        secret_name: Name of secret to fetch.

    Note:
        The returned secret is not cached, so, calling this function again
        may do a new network roundtrip.

    Note:
        When used, if `robocorp.log` is in the environment, all the values
        gotten will be automatically hidden from the logs.
        i.e.: For each value, `log.hide_from_output(value)` will be called.

    Returns:
        The container for the secret (which has key-value pairs).

    Raises:
        RobocorpVaultError: Error with API request or response payload.
    """
    try:
        from robocorp import log  # type: ignore [attr-defined]

        ctx = log.suppress_variables()
        has_log = True
    except ImportError:
        pass  # If robocorp.log is not being used that's OK.
        ctx = nullcontext()
        has_log = False

    with ctx:
        vault = _get_vault()

        # Note: secrets are always gotten from the backend when requested
        # (so any updates will be gotten in a new `get_secret` call).
        secret = vault.get_secret(secret_name)

        if has_log:
            # There's no caching in place, so, on any new call it's possible
            # that values changed, so, call this every time.
            _ignore_secret_values(secret)

    return secret


def set_secret(secret: SecretContainer) -> None:
    """Overwrite an existing secret with new values.

    Note:
        Only allows modifying existing secrets, and replaces
          all values contained within it.

    Note:
        When used, if `robocorp.log` is in the environment, all the values
        set will be automatically hidden from the logs.
        i.e.: For each value, `log.hide_from_output(value)` will be called.

    Args:
        secret: the secret object which was mutated.
    """
    try:
        from robocorp import log  # type: ignore [attr-defined]

        ctx = log.suppress_variables()
        has_log = True
    except ImportError:
        pass  # If robocorp.log is not being used that's OK.
        ctx = nullcontext()
        has_log = False

    with ctx:
        vault = _get_vault()
        vault.set_secret(secret)

        if has_log:
            # When it's set it's expected that some value was changed, so,
            # start hiding it from the logs.
            # Note: users should've actually done that already, but doing
            # it again is harmless.
            _ignore_secret_values(secret)


def _ignore_secret_values(secret):
    from robocorp import log

    for value in secret.values():
        s = str(value)
        log.hide_from_output(s)

        # Now, also take care of the case where the user does a repr(value)
        # and not just str(value) as in some places it's the repr(value)
        # that'll appear in the logs.
        r = repr(value)
        if r.startswith("'") and r.endswith("'"):
            r = r[1:-1]
        if r != s:
            log.hide_from_output(r)
            log.hide_from_output(r.replace("\\", "\\\\"))


__all__ = ["get_secret", "set_secret"]
