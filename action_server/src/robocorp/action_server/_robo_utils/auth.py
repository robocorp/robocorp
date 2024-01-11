def generate_api_key():
    import secrets

    return secrets.token_urlsafe(32)
