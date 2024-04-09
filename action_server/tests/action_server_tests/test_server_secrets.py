from robocorp.action_server._selftest import ActionServerClient, ActionServerProcess

# Used in test so that the information is static (no random key or iv).
USE_STATIC_INFO = False


def test_secrets_encrypted(
    action_server_process: ActionServerProcess,
    client: ActionServerClient,
    datadir,
):
    import base64
    import json
    import os

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    pack = datadir / "pack_encryption"

    keys = [AESGCM.generate_key(bit_length=256), AESGCM.generate_key(bit_length=256)]
    if USE_STATIC_INFO:
        keys = [b"a" * len(keys[0])]

    # ACTION_SERVER_DECRYPT_INFORMATION: Contains information on what is passed
    # as encrypted.
    # Note: x-action-context is "special" in that it's a header that can be sent to
    # the action server over multiple parts (x-action-context-1, x-action-context-2, ...)
    # the result of all the parts will be decoded.
    #
    # ACTION_SERVER_DECRYPT_KEYS: The keys that can be used to decrypt (base-64
    # version of the actual bytes used to encrypt).
    env = dict(
        ACTION_SERVER_DECRYPT_INFORMATION=json.dumps(["header:x-action-context"]),
        ACTION_SERVER_DECRYPT_KEYS=json.dumps(
            [base64.b64encode(k).decode("ascii") for k in keys]
        ),
    )

    action_server_process.start(
        cwd=pack,
        actions_sync=True,
        db_file="server.db",
        lint=True,
        env=env,
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

    found = client.post_get_str(
        "api/actions/pack-encryption/get-private/run",
        {"name": "Foo"},
        headers={"x-action-context": ctx_info},
    )
    assert "my-secret-value" == json.loads(found)


def test_secrets_not_encrypted(
    action_server_process: ActionServerProcess,
    client: ActionServerClient,
    datadir,
):
    # Verify that things work if the X-Action-Context is not encrypted.
    import base64
    import json

    pack = datadir / "pack_encryption"

    action_server_process.start(
        cwd=pack,
        actions_sync=True,
        db_file="server.db",
        lint=True,
    )

    action_server_context: str = json.dumps(
        {"secrets": {"private_info": "my-secret-value"}}
    )
    ctx_info: str = base64.b64encode(action_server_context.encode("utf-8")).decode(
        "ascii"
    )

    found = client.post_get_str(
        "api/actions/pack-encryption/get-private/run",
        {"name": "Foo"},
        headers={"x-action-context": ctx_info},
    )
    assert "my-secret-value" == json.loads(found)
