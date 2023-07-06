# ruff: noqa


def call_vault():
    from robocorp import vault

    secrets = vault.get_secret("secrets")
    for secret_key, secret_val in secrets.items():
        a = str(secret_val)
        b = repr(secret_val)

    return secrets
