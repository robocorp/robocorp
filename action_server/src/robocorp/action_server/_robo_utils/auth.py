import os
from typing import Optional
from pathlib import Path


def generate_api_key():
    import secrets

    return secrets.token_urlsafe(32)


def get_api_key(datadir: Path) -> str:
    api_key_path = os.path.join(datadir, ".api_key")

    try:
        with open(api_key_path, "r") as file:
            api_key = file.read()
    except Exception:
        api_key = ""

    if len(api_key) == 0:
        api_key = generate_api_key()

        with open(api_key_path, "w") as file:
            file.write(api_key)

    return api_key
