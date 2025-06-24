from contextlib import nullcontext
from functools import lru_cache
from typing import Any

from ._errors import RobocorpVaultError
from ._secrets import SecretContainer

__version__ = "1.3.9"
version_info = [int(x) for x in __version__.split(".")]


@lru_cache
def _get_vault():
    from ._vault import Vault

    return Vault()


def get_secret(name: str, hide: bool = True) -> SecretContainer:
    """Get a secret with the given name.

    Args:
        name: Name of secret to fetch
        hide: Hide secret values from log output

    Note:
        If `robocorp.log` is available in the environment, the `hide` argument
        controls if the given values are automatically hidden in the log
        output.

    Returns:
        Secret container of name, description, and key-value pairs

    Raises:
        RobocorpVaultError: Error with API request or response payload.
    """
    with _suppress_variables():
        vault = _get_vault()
        secret = vault.get_secret(name)

        if hide:
            _hide_secret_values(secret)

        return secret


def set_secret(secret: SecretContainer, hide: bool = True) -> None:
    """Set a secret value using an existing container.

    **Note:** If the secret already exists, all contents are replaced.

    Args:
        secret: Secret container, created manually or returned by `get_secret`
        hide: Hide secret values from log output

    Note:
        If `robocorp.log` is available in the environment, the `hide` argument
        controls if the given values are automatically hidden in the log
        output.

    Raises:
        RobocorpVaultError: Error with API request or response payload
    """
    with _suppress_variables():
        vault = _get_vault()
        vault.set_secret(secret)

        if hide:
            _hide_secret_values(secret)


def create_secret(
    name: str,
    values: dict[str, Any],
    description: str = "",
    exist_ok: bool = False,
    hide: bool = True,
) -> SecretContainer:
    """Create a new secret, or overwrite an existing one.

    Args:
        name: Name of secret
        values: Mapping of secret keys and values
        description: Optional description for secret
        exist_ok: Overwrite existing secret
        hide: Hide secret values from log output

    Note:
        If `robocorp.log` is available in the environment, the `hide` argument
        controls if the given values are automatically hidden in the log
        output.

    Returns:
        Secret container of name, description, and key-value pairs

    Raises:
        RobocorpVaultError: Error with API request or response payload
    """
    with _suppress_variables():
        vault = _get_vault()
        if not exist_ok:
            try:
                vault.get_secret(name)
            except Exception:
                pass
            else:
                raise RobocorpVaultError(f"Secret with name '{name}' already exists")

        secret = SecretContainer(
            name=name,
            description=description,
            values=values,
        )
        set_secret(secret, hide=hide)
        return secret


def _suppress_variables():
    try:
        from robocorp import log  # type: ignore [attr-defined]

        return log.suppress_variables()
    except ImportError:
        return nullcontext()


def _hide_secret_values(secret):
    try:
        from robocorp import log
    except ImportError:
        return

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


__all__ = [
    "get_secret",
    "set_secret",
    "create_secret",
    "SecretContainer",
    "RobocorpVaultError",
]
