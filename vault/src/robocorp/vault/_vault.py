import logging
import os

from ._adapters import BaseSecretManager, FileSecrets, RobocorpVault
from ._secrets import SecretContainer
from ._utils import import_by_name, required_env


class Vault:
    def __init__(self, *args, **kwargs):
        """The selected adapter can be set with the environment variable.

        Use the environment variable ``RC_VAULT_SECRET_MANAGER``, or the
        argument ``default_adapter``.
        Defaults to Robocorp Vault if not defined.

        All other library arguments are passed to the adapter.

        Args:
            default_adapter: Override default secret adapter

        """
        self.logger = logging.getLogger(__name__)

        default = kwargs.pop("default_adapter", RobocorpVault)
        if "RC_VAULT_SECRET_MANAGER" in os.environ:
            adapter = required_env("RC_VAULT_SECRET_MANAGER", default)
        elif "RPA_SECRET_MANAGER" in os.environ:  # Backward-compatibility
            adapter = required_env("RPA_SECRET_MANAGER", default)
        else:
            adapter = default

        self._adapter_factory = self._create_factory(adapter, args, kwargs)
        self._adapter = None

    @property
    def adapter(self) -> BaseSecretManager:
        if self._adapter is None:
            self._adapter = self._adapter_factory()

        return self._adapter

    def _create_factory(self, adapter, args, kwargs):
        if isinstance(adapter, str):
            if adapter in ("FileSecrets", "RPA.Robocorp.Vault.FileSecrets"):
                adapter = FileSecrets
            else:
                try:
                    adapter = import_by_name(adapter, __name__)
                except Exception as e:
                    raise ValueError(
                        f"RC_VAULT_SECRET_MANAGER environment variable seems to "
                        f"have a wrong value: {adapter!r}.\n"
                        f'It should be unset to load from Control Room, "FileSecrets" '
                        f'to load from a file or the name of the "BaseSecretManager" '
                        f"implementation class."
                    ) from e

        if not issubclass(adapter, BaseSecretManager):
            raise ValueError(
                f"Adapter '{adapter}' does not inherit from BaseSecretManager"
            )

        def factory():
            return adapter(*args, **kwargs)

        return factory

    def get_secret(self, secret_name: str) -> SecretContainer:
        """Read a secret from the configured source, e.g. Robocorp Vault.

        Args:
            secret_name: Name of secret.

        Returns:
            `SecretContainer` object.
        """
        return self.adapter.get_secret(secret_name)

    def set_secret(self, secret: SecretContainer) -> None:
        """Create secret or overwrite existing.

        Args:
            secret: `SecretContainer` object, from e.g. `get_secret`.
        """
        self.adapter.set_secret(secret)
