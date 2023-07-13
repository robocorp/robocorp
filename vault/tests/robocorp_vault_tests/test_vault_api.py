import logging
import random
import sys
import time

import pytest


@pytest.fixture
def clear_cached_vault():
    from robocorp import vault

    vault._get_vault.cache_clear()
    yield
    vault._get_vault.cache_clear()


def test_vault_api(monkeypatch, datadir, clear_cached_vault):
    from robocorp import vault

    monkeypatch.setenv("RC_VAULT_SECRET_MANAGER", "FileSecrets")
    monkeypatch.setenv("RC_VAULT_SECRETS_FILE", str(datadir / "secrets.json"))

    secret_container = vault.get_secret("windows")
    secret_container[10] = 10

    # Key types are always converted to str internally.
    assert 10 in secret_container
    assert "10" in secret_container
    assert secret_container[10] == 10

    vault.set_secret(secret_container)
    vault._get_vault.cache_clear()

    secret_container = vault.get_secret("windows")
    assert 10 in secret_container
    assert "10" in secret_container
    assert secret_container[10] == 10

    vault.create_secret(
        "generated",
        {"a-key": "a-value"},
        description="Some sort of secret",
    )

    secret_container = vault.get_secret("generated")
    assert secret_container.name == "generated"
    assert len(secret_container) == 1
    assert secret_container["a-key"] == "a-value"

    with pytest.raises(vault.RobocorpVaultError):
        vault.create_secret("generated", {})

    vault.create_secret("generated", {"a-key": "another-value"}, exist_ok=True)
    secret_container = vault.get_secret("generated")
    assert secret_container["a-key"] == "another-value"


@pytest.fixture
def log_to_stderr():
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setLevel(logging.ERROR)  # logging.DEBUG would actually print the token...
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    yield
    logger.removeHandler(handler)


def test_vault_integrated(
    monkeypatch, clear_cached_vault, ci_credentials, rcc, log_to_stderr
):
    monkeypatch.delenv("RC_VAULT_SECRET_MANAGER", None)
    monkeypatch.delenv("RC_VAULT_SECRETS_FILE", None)

    result = rcc.add_credentials(ci_credentials)
    assert result.success
    assert rcc.credentials_valid()

    result = rcc.cloud_list_workspaces()
    assert result.success

    workspaces = result.result
    if not workspaces:
        raise AssertionError("Expected to have CI Workspace available.")
    workspaces = [ws for ws in workspaces if ws.workspace_name == "CI workspace"]
    if not workspaces:
        raise AssertionError("Expected to have CI Workspace available.")

    ws = workspaces[0]

    action_result_authorize = rcc.cloud_authorize_token(ws.workspace_id)

    assert len(action_result_authorize.result["token"]) > 10
    assert len(action_result_authorize.result["endpoint"]) > 10

    from robocorp import vault

    monkeypatch.setenv("RC_API_SECRET_HOST", action_result_authorize.result["endpoint"])
    monkeypatch.setenv("RC_API_SECRET_TOKEN", action_result_authorize.result["token"])
    monkeypatch.setenv("RC_WORKSPACE_ID", ws.workspace_id)
    secret_container = vault.get_secret("ROBOCORP_VAULT_TEST")

    assert "VAULT_KEY1" in secret_container
    assert "vault_key2" in secret_container
    for i in range(3):
        new_value = secret_container["vault_key3"] = str(time.time())
        vault.set_secret(secret_container)

        vault._get_vault.cache_clear()
        found = vault.get_secret("ROBOCORP_VAULT_TEST")["vault_key3"]

        # This is more complicated because when running in the ci we have a test
        # on linux/window/mac os at the same time and a single resource (the vault)
        # so, if we don't have the same value wait a bit and retry.
        if found == new_value:
            break
        if i == 2:
            # Fail in the last attempt.
            assert found == new_value
        else:
            # Sleep up to 3 seconds before retrying.
            time.sleep(random.random() * 3)
