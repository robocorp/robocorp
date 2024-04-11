# Used in test so that the information is static (no random key or iv).
USE_STATIC_INFO = False


def test_secrets_encryption_raw() -> None:
    import os

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    data = b"a secret message"
    key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, data, None)
    assert aesgcm.decrypt(nonce, ct, None) == data


def test_action_context() -> None:
    import base64
    import json
    import os

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    from robocorp.actions._action_context import ActionContext

    keys = [AESGCM.generate_key(bit_length=256), AESGCM.generate_key(bit_length=256)]
    if USE_STATIC_INFO:
        keys = [b"a" * len(keys[0])]

    env = dict(
        ACTION_SERVER_DECRYPT_INFORMATION=json.dumps(["header:x-action-context"]),
        ACTION_SERVER_DECRYPT_KEYS=json.dumps(
            [base64.b64encode(k).decode("ascii") for k in keys]
        ),
    )

    data: bytes = json.dumps({"secrets": {"private_info": "my-secret-value"}}).encode(
        "utf-8"
    )
    aesgcm = AESGCM(keys[0])
    nonce = os.urandom(12)
    if USE_STATIC_INFO:
        nonce = b"b" * len(nonce)

    encrypted_data = aesgcm.encrypt(nonce, data, None)

    action_server_context = {
        "cipher": base64.b64encode(encrypted_data).decode("ascii"),
        "algorithm": "aes256-cdc",
        "iv": base64.b64encode(nonce).decode("ascii"),
    }

    ctx_info: str = base64.b64encode(
        json.dumps(action_server_context).encode("utf-8")
    ).decode("ascii")

    ctx = ActionContext(ctx_info, env=env)
    assert ctx.value == {"secrets": {"private_info": "my-secret-value"}}
