<!-- markdownlint-disable -->

# API Overview

## Modules

- [`robocorp.vault`](./robocorp.vault.md#module-robocorpvault)

## Classes

- [`_errors.RobocorpVaultError`](./robocorp.vault._errors.md#class-robocorpvaulterror): Raised when there's problem with reading from Robocorp Vault.
- [`_secrets.SecretContainer`](./robocorp.vault._secrets.md#class-secretcontainer): Container for a secret with name, description, and multiple key-value pairs.

## Functions

- [`vault.create_secret`](./robocorp.vault.md#function-create_secret): Create a new secret, or overwrite an existing one.
- [`vault.get_secret`](./robocorp.vault.md#function-get_secret): Get a secret with the given name.
- [`vault.set_secret`](./robocorp.vault.md#function-set_secret): Set a secret value using an existing container.
