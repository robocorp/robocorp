# robocorp-vault

`robocorp-vault` is a library that provides read and write access to the [Vault](https://robocorp.com/docs/development-guide/variables-and-secrets/vault) in Robocorp Control Room, which can be used to store and retrieve secret values such as passwords.

## Getting started

A secret consists of a name, an optional description, and a map of keys and values. For instance, one secret can be login credentials for a website, which includes both a username and a password:

```python
from robocorp.tasks import task
from robocorp import vault

@task
def inspect_secret():
    secret = vault.get_secret("login_credentials")
    print("Secret name:", secret.name)
    print("Secret description:", secret.description)
    print("Secret keys:", secret.keys())
    print("Secret value:", secret["username"])
```

## Guides

- [Local development](https://github.com/robocorp/robocorp/blob/master/vault/docs/guides/00-local-development.md)
- [Hiding values](https://github.com/robocorp/robocorp/blob/master/vault/docs/guides/01-hiding-values.md)
- [Modifying secrets](https://github.com/robocorp/robocorp/blob/master/vault/docs/guides/02-modifying-secrets.md)

Further user guides and tutorials can be found in [Robocorp Docs](https://robocorp.com/docs).

## API Reference

Explore our [API](https://github.com/robocorp/robocorp/blob/master/vault/docs/api/README.md) for extensive documentation.

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/vault/docs/CHANGELOG.md).
