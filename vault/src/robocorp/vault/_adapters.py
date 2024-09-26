import base64
import binascii
import copy
import json
import logging
import os
from abc import ABCMeta, abstractmethod
from typing import Callable, Tuple

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ._errors import RobocorpVaultError
from ._requests import HTTPError, Requests
from ._secrets import SecretContainer
from ._utils import required_env, resolve_path, url_join


class BaseSecretManager(metaclass=ABCMeta):
    """Abstract class for secrets management.

    Should be used as a base-class for any adapter implementation.
    """

    @abstractmethod
    def get_secret(self, secret_name) -> SecretContainer:
        """Return ``SecretContainer`` object with given name."""

    @abstractmethod
    def set_secret(self, secret: SecretContainer):
        """Set a secret with a new value."""


class FileSecrets(BaseSecretManager):
    """Adapter for secrets stored in a database file.

    Supports only plaintext secrets, and should be used mainly for debugging.

    The path to the secrets file can be set with the
    environment variable ``RC_VAULT_SECRETS_FILE``, or as
    an argument to the library.

    The format of the secrets file should be one of the following:

    .. code-block:: JSON

      {
        "name1": {
          "key1": "value1",
          "key2": "value2"
        },
        "name2": {
          "key1": "value1"
        }
      }

    OR

    .. code-block:: YAML

      name1:
        key1: value1
        key2: value2
      name2:
        key1: value1
    """

    def __init__(self, secret_file="secrets.json"):
        self.logger = logging.getLogger(__name__)

        if "RC_VAULT_SECRETS_FILE" in os.environ:
            path = required_env("RC_VAULT_SECRETS_FILE", secret_file)
        elif "RPA_SECRET_FILE" in os.environ:  # Backward-compatibility
            path = required_env("RPA_SECRET_FILE", secret_file)
        else:
            path = secret_file

        self.logger.info("Resolving path: %s", path)
        self.path = resolve_path(path)

        extension = self.path.suffix
        self._loader, self._dumper = self._get_serializer(extension)

    def _get_serializer(self, extension: str) -> Tuple[Callable, Callable]:
        if extension == ".json":
            return (json.load, json.dump)

        if extension == ".yaml":
            import yaml

            return (yaml.safe_load, yaml.dump)

        # NOTE(cmin764): This will raise instead of returning an empty secrets object
        #  because it is wrong starting from the "env.json" configuration level.
        raise ValueError(
            f"Local vault secrets file extension {extension!r} not supported."
        )

    def _load(self):
        """Load secrets file."""
        with open(self.path, encoding="utf-8") as fd:
            data = self._loader(fd)

        if not isinstance(data, dict):
            raise ValueError(f"Expected dictionary, was '{type(data)}'")

        return data

    def _save(self, data):
        """Save the secrets content to disk."""
        if not isinstance(data, dict):
            raise ValueError(f"Expected dictionary, was '{type(data)}'")

        with open(self.path, "w", encoding="utf-8") as f:
            self._dumper(data, f, indent=4)

    def get_secret(self, secret_name: str) -> SecretContainer:
        """Get secret defined with given name from file.

        Args:
            secret_name: Name of secret to fetch
        Returns:
            SecretContainer: SecretContainer object

        Raises:
            KeyError: No secret with given name

        """
        values = self._load().get(secret_name)
        if values is None:
            raise KeyError(f"Undefined secret: {secret_name}")

        return SecretContainer(secret_name, "", values)

    def set_secret(self, secret: SecretContainer) -> None:
        """Set the secret value in the local Vault with the given
        ``SecretContainer`` object.

        Args:
            secret: A ``SecretContainer`` object.

        Raises:
            IOError: Writing the local vault failed.
            ValueError: Writing the local vault failed.

        """
        data = self._load()
        data[secret.name] = dict(secret)
        self._save(data)


class RobocorpVault(BaseSecretManager):
    """Adapter for secrets stored in Robocorp Vault.

    The following environment variables should exist:

    - RC_API_SECRET_HOST:   URL to Robocorp Secret API
    - RC_API_SECRET_TOKEN:  API token with access to Robocorp Secret API
    - RC_WORKSPACE_ID:      Robocorp Workspace ID

    If the robot run is started from the Robocorp Control Room these environment
    variables will be configured automatically.

    """

    ENCRYPTION_SCHEME = "robocloud-vault-transit-v2"

    def __init__(self, *args, **kwargs):
        # pylint: disable=unused-argument
        self.logger = logging.getLogger(__name__)
        # Environment variables set by runner
        host = required_env("RC_API_SECRET_HOST")
        token = required_env("RC_API_SECRET_TOKEN")
        workspace = required_env("RC_WORKSPACE_ID")
        headers = {"Authorization": f"Bearer {token}"}
        endpoint = url_join(
            host,
            "secrets-v1",
            "workspaces",
            workspace,
            "secrets",
            "",  # Ensure endpoint has trailing slash
        )
        self._client = Requests(route_prefix=endpoint, default_headers=headers)
        # Generated lazily on request
        self.__private_key = None
        self.__public_bytes = None

    @property
    def _private_key(self):
        """Cryptography private key object."""
        if self.__private_key is None:
            self.__private_key = rsa.generate_private_key(
                public_exponent=65537, key_size=4096, backend=default_backend()
            )

        return self.__private_key

    @property
    def _public_bytes(self):
        """Serialized public key bytes."""
        if self.__public_bytes is None:
            self.__public_bytes = base64.b64encode(
                self._private_key.public_key().public_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )

        return self.__public_bytes

    def get_secret(self, secret_name: str) -> SecretContainer:
        """Get secret defined with given name from Robocorp Vault.

        Args:
            secret_name: Name of secret to fetch
        Returns:
            SecretContainer object

        Raises:
            RobocorpVaultError: Error with API request or response payload
        """
        params = {
            "encryptionScheme": self.ENCRYPTION_SCHEME,
            "publicKey": self._public_bytes,
        }

        try:
            response = self._client.get(secret_name, params=params)
            payload = response.json()
            payload = self._decrypt_payload(payload)
            return SecretContainer(
                name=payload["name"],
                description=payload["description"],
                values=payload["values"],
            )
        except InvalidTag as err:
            raise RobocorpVaultError("Failed to validate authentication tag") from err
        except HTTPError as err:
            if err.status_code == 403:
                message = "Not authorized to read secret. Is your token valid?"
            elif err.status_code == 404:
                message = f"No secret with name '{secret_name}' available"
            else:
                message = str(err)
            raise RobocorpVaultError(message) from err
        except RecursionError as err:
            message = (
                "Infinite recursion detected due to SSL patching bug, please"
                " remove `truststore` from your dependencies file and opt in for `uv`"
                " instead of `pip`"
            )
            raise RobocorpVaultError(message) from err
        except Exception as err:
            raise RobocorpVaultError(str(err)) from err

    def _decrypt_payload(self, payload):
        payload = copy.deepcopy(payload)

        fields = payload.pop("encryption", None)
        if fields is None:
            raise KeyError("Missing encryption fields from response")

        scheme = fields["encryptionScheme"]
        if scheme != self.ENCRYPTION_SCHEME:
            raise ValueError(f"Unexpected encryption scheme: {scheme}")

        aes_enc = base64.b64decode(fields["encryptedAES"])
        aes_tag = base64.b64decode(fields["authTag"])
        aes_iv = base64.b64decode(fields["iv"])

        # Decrypt AES key using our private key
        aes_key = self._private_key.decrypt(
            aes_enc,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # Decrypt actual value using decrypted AES key
        ciphertext = base64.b64decode(payload.pop("value")) + aes_tag
        data = AESGCM(aes_key).decrypt(binascii.hexlify(aes_iv), ciphertext, b"")
        payload["values"] = json.loads(data)

        return payload

    def set_secret(self, secret: SecretContainer) -> None:
        """Set the secret value in the Vault.

        Note:
            The secret possibly consists of multiple key-value pairs,
            which will all be overwritten with the values given here.
            So don't try to update only one item of the secret, update all of them.

        Args:
            secret: A ``SecretContainer`` object

        """
        value, aes_iv, aes_key, aes_tag = self._encrypt_secret_value_with_aes(secret)
        pub_key = self.get_publickey()
        aes_enc = self._encrypt_aes_key_with_public_rsa(aes_key, pub_key)

        payload = {
            "encryption": {
                "authTag": aes_tag.decode(),
                "encryptedAES": aes_enc.decode(),
                "encryptionScheme": self.ENCRYPTION_SCHEME,
                "iv": aes_iv.decode(),
            },
            "name": secret.name,
            "value": value.decode(),
            "description": secret.description,
        }

        try:
            self._client.put(secret.name, json=payload)
        except HTTPError as err:
            if err.status_code == 403:
                message = "Not authorized to write secret. Is your token valid?"
            elif err.status_code == 404:
                message = f"No secret with name '{secret.name}' available"
            else:
                message = str(err)
            raise RobocorpVaultError(message) from err
        except Exception as err:
            raise RobocorpVaultError(str(err)) from err

    def get_publickey(self) -> bytes:
        """Get the public key for AES encryption with the existing token."""
        try:
            response = self._client.get("publicKey")
            return response.content
        except HTTPError as err:
            if err.status_code == 403:
                message = "Not authorized to read public key. Is your token valid?"
            else:
                message = str(err)
            raise RobocorpVaultError(message) from err
        except Exception as err:
            raise RobocorpVaultError(str(err)) from err

    @staticmethod
    def _encrypt_secret_value_with_aes(
        secret: SecretContainer,
    ) -> Tuple[bytes, bytes, bytes, bytes]:
        def generate_aes_key() -> Tuple[bytes, bytes]:
            aes_key = AESGCM.generate_key(256)
            aes_iv = os.urandom(16)
            return aes_key, aes_iv

        def split_auth_tag_from_encrypted_value(
            encrypted_value: bytes,
        ) -> Tuple[bytes, bytes]:
            """AES auth tag is the last 16 bytes of the AES encrypted value.

            Split the tag from the value, as that is required for the API.

            """
            aes_tag = encrypted_value[-16:]
            trimmed_encrypted_value = encrypted_value[:-16]
            return trimmed_encrypted_value, aes_tag

        value = json.dumps(dict(secret)).encode()

        aes_key, aes_iv = generate_aes_key()
        encrypted_value = AESGCM(aes_key).encrypt(aes_iv, value, b"")
        encrypted_value, aes_tag = split_auth_tag_from_encrypted_value(encrypted_value)

        return (
            base64.b64encode(encrypted_value),
            base64.b64encode(aes_iv),
            aes_key,
            base64.b64encode(aes_tag),
        )

    @staticmethod
    def _encrypt_aes_key_with_public_rsa(aes_key: bytes, public_rsa: bytes) -> bytes:
        pub_decoded = base64.b64decode(public_rsa)
        public_key = serialization.load_der_public_key(pub_decoded)

        aes_enc = public_key.encrypt(  # type: ignore [union-attr]
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        return base64.b64encode(aes_enc)
