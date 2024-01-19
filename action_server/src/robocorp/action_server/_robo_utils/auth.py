from pathlib import Path


def generate_api_key():
    import secrets

    return secrets.token_urlsafe(32)


def get_api_key(datadir: Path) -> str:
    api_key_path = datadir / ".api_key"

    try:
        api_key = api_key_path.read_text("utf-8")
    except Exception:
        api_key = ""

    if len(api_key) == 0:
        api_key = generate_api_key()
        api_key_path.write_text(api_key, "utf-8")

    return api_key
