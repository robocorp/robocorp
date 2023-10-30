import sys

import pytest


@pytest.fixture
def add_log_to_env():
    try:
        from robocorp import log  # noqa

        raise ImportError()
    except ImportError:
        # On the CI logging is not in the env (because it's not a mandatory
        # dep), so add it.
        from pathlib import Path

        from robocorp import vault

        p = Path(vault.__file__)
        log_src = p.parent.parent.parent.parent.parent / "log" / "src"
        import sys

        sys.path.append(str(log_src))
        from robocorp import log  # noqa


@pytest.fixture
def check_secrets_mod(datadir):
    sys.path.append(str(datadir))
    import check_secrets  # type: ignore # @UnresolvedImport

    yield check_secrets
    sys.path.remove(str(datadir))


@pytest.fixture
def clear_cached_vault():
    from robocorp import vault

    vault._get_vault.cache_clear()
    yield
    vault._get_vault.cache_clear()


def test_secrets_hidden(
    check_secrets_mod, monkeypatch, datadir, clear_cached_vault, capsys, add_log_to_env
):
    from importlib import reload

    from robocorp.log import verify_log_messages_from_stream

    monkeypatch.setenv("RC_VAULT_SECRET_MANAGER", "FileSecrets")
    monkeypatch.setenv("RC_VAULT_SECRETS_FILE", str(datadir / "secrets.json"))

    from io import StringIO

    from robocorp.log import setup_auto_logging

    from robocorp import log

    s = StringIO()

    def on_write(msg):
        s.write(msg)

    with setup_auto_logging():
        check_secrets_mod = reload(check_secrets_mod)
        with log.add_in_memory_log_output(
            on_write,
        ):
            log.start_run("Robot1")
            log.start_task("Simple Task", "task_mod", __file__, 0)

            secrets = check_secrets_mod.call_vault()

            log.end_task("Simple Task", "task_mod", "PASS", "Ok")
            log.end_run("Robot1", "PASS")

    s.seek(0)
    for msg in verify_log_messages_from_stream(s, [], []):
        for _secret_key, secret_val in secrets.items():
            assert str(secret_val) not in str(msg)
            assert repr(secret_val) not in str(msg)
            assert "á" not in str(msg)  # part of one of the secrets.
