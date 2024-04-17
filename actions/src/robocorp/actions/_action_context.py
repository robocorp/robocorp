import base64
import json
import os
from typing import Dict, List, Optional

from robocorp.actions._protocols import JSONValue
from robocorp.actions._request import Request


def _get_str_list_from_env(env_name: str, env) -> List[str]:
    # Verify if it's an encrypted header.
    in_env: str = env.get(env_name, "")
    if not in_env:
        return []

    try:
        lst_info_to_decrypt = json.loads(in_env)
    except Exception:
        raise RuntimeError(
            f"Error: the {env_name} is expected to be a json list of strings, "
            f"however it cannot be interpreted as json. Found: {in_env}"
        )
    if not isinstance(lst_info_to_decrypt, list):
        raise RuntimeError(
            f"Error: the {env_name} is expected to be a json list (of strings). "
            f"Found: {lst_info_to_decrypt}."
        )

    for entry in lst_info_to_decrypt:
        if not isinstance(entry, str):
            raise RuntimeError(
                f"Error: the {env_name} is expected to be a json list containing "
                f"only strings. Found: {lst_info_to_decrypt}."
            )

    return lst_info_to_decrypt


class ActionContext:
    """
    This is data received as input which may or may not be encrypted.

    When a user requests the actual value, it'll be decrypted if that's the case.
    """

    _encrypted: bool

    def __init__(self, data: str, env: Optional[Dict[str, str]] = None):
        """
        Args:
            data: The data requested from that source.
                If encrypted, must be something as:

                base64(json.dumps({
                   cipher: blob_of_data
                   algorithm: "aes256-gcm"
                   iv: nonce
                }))

                Otherwise the payload should be passed directly,
                which should be something as:
                    base64(json.dumps({
                      'secrets': {'secret_name': 'secret_value'}
                    }))

            path: the payload is expected to be a json object, and the
                path defined here maps to how to get that value.

                i.e.: if the payload has:

                {
                  'secrets': {'secret_name': 'secret_value'}
                }

                The path to access the secret_name would be:
                'secrets/secret_name'.

        """
        self._env = env
        loaded_data = json.loads(base64.b64decode(data.encode("ascii")).decode("utf-8"))
        if not isinstance(loaded_data, dict):
            raise RuntimeError(
                "Expected 'X-Action-Context' header to have json contents."
            )

        # Ok, we have the basic info, now, this info may be encrypted or not
        # (if it's encrypted we have 'cipher', 'algorithm' and 'iv', otherwise
        # we have the raw info directly -- such as 'secrets').
        if (
            "cipher" in loaded_data
            and "algorithm" in loaded_data
            and "iv" in loaded_data
        ):
            self._encrypted = True
            self._encrypted_data: Dict[str, JSONValue] = loaded_data
        else:
            self._encrypted = False
            self._raw_data: Dict[str, JSONValue] = loaded_data
            self._hide_secrets()

    @property
    def value(self) -> JSONValue:
        # Data already decrypted
        try:
            return self._raw_data
        except AttributeError:
            pass

        if not self._encrypted:
            raise RuntimeError("Expected data to be encrypted if it reached here!")

        from robocorp import log

        with log.suppress():
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM

            keys = _get_str_list_from_env(
                "ACTION_SERVER_DECRYPT_KEYS", env=self._env or os.environ
            )

            if not keys:
                raise RuntimeError(
                    "The information in the X-Action-Server seems to be encrypted, but decryption keys are not available in ACTION_SERVER_DECRYPT_KEYS."
                )

            cipher = self._encrypted_data["cipher"]
            algorithm = self._encrypted_data["algorithm"]
            iv = self._encrypted_data["iv"]
            auth_tag = self._encrypted_data.get("auth-tag")

            if not isinstance(cipher, str):
                raise RuntimeError(
                    f"Expected the cipher to be a str. Found: {cipher!r}"
                )

            if not isinstance(algorithm, str):
                raise RuntimeError(
                    f"Expected the algorithm to be a str. Found: {algorithm!r}"
                )

            if not isinstance(iv, str):
                raise RuntimeError(f"Expected the iv to be a str. Found: {iv!r}")

            try:
                cipher_decoded_base_64: bytes = base64.b64decode(cipher)
            except Exception:
                raise RuntimeError(
                    "Unable to decode the 'cipher' field passed to X-Action-Context as base64."
                )

            try:
                iv_decoded_base_64: bytes = base64.b64decode(iv)
            except Exception:
                raise RuntimeError(
                    "Unable to decode the 'iv' field passed to X-Action-Context as base64."
                )

            if not auth_tag:
                auth_tag_decoded_base_64: bytes = b""
            else:
                if isinstance(auth_tag, str):
                    try:
                        auth_tag_decoded_base_64 = base64.b64decode(auth_tag)
                    except Exception:
                        raise RuntimeError(
                            "Unable to decode the 'auth-tag' field passed to X-Action-Context as base64."
                        )
                else:
                    raise RuntimeError(
                        f"Expected the auth-tag to be a str. Found: {auth_tag!r}"
                    )

            if algorithm != "aes256-gcm":
                raise RuntimeError(
                    f"Unable to recognize X-Action-Context encryption algorithm: {algorithm}"
                )

            for key in keys:
                k: bytes = base64.b64decode(key.encode("ascii"))
                aesgcm = AESGCM(k)
                try:
                    raw_data = aesgcm.decrypt(
                        iv_decoded_base_64,
                        cipher_decoded_base_64,
                        auth_tag_decoded_base_64,
                    )
                    break
                except Exception:
                    continue
            else:
                raise RuntimeError(
                    "It was not possible to decode the X-Action-Context header with any of the available keys."
                )

            self._raw_data = json.loads(raw_data)
            self._hide_secrets()

        return self._raw_data

    def _hide_secrets(self):
        secrets = self._raw_data.get("secrets")
        if secrets and isinstance(secrets, dict):
            from robocorp import log

            for secret_value in secrets.values():
                if isinstance(secret_value, str):
                    log.hide_from_output(secret_value)
                    log.hide_from_output(repr(secret_value))

    @classmethod
    def from_request(cls, request: Optional[Request]) -> Optional["ActionContext"]:
        if not request:
            return None
        data = request.headers.get("x-action-context")
        if data is None:
            return None
        return ActionContext(data)
