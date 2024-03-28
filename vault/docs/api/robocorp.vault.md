<!-- markdownlint-disable -->

# module `robocorp.vault`

# Functions

______________________________________________________________________

## `get_secret`

Get a secret with the given name.

**Args:**

- <b>`name`</b>:  Name of secret to fetch
- <b>`hide`</b>:  Hide secret values from log output

**Note:**

> If `robocorp.log` is available in the environment, the `hide` argument controls if the given values are automatically hidden in the log output.

**Returns:**
Secret container of name, description, and key-value pairs

**Raises:**

- <b>`RobocorpVaultError`</b>:  Error with API request or response payload.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/__init__.py#L19)

```python
get_secret(name: str, hide: bool = True) → SecretContainer
```

______________________________________________________________________

## `set_secret`

Set a secret value using an existing container.

**Note:** If the secret already exists, all contents are replaced.

**Args:**

- <b>`secret`</b>:  Secret container, created manually or returned by `get_secret`
- <b>`hide`</b>:  Hide secret values from log output

**Note:**

> If `robocorp.log` is available in the environment, the `hide` argument controls if the given values are automatically hidden in the log output.

**Raises:**

- <b>`RobocorpVaultError`</b>:  Error with API request or response payload

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/__init__.py#L47)

```python
set_secret(secret: SecretContainer, hide: bool = True) → None
```

______________________________________________________________________

## `create_secret`

Create a new secret, or overwrite an existing one.

**Args:**

- <b>`name`</b>:  Name of secret
- <b>`values`</b>:  Mapping of secret keys and values
- <b>`description`</b>:  Optional description for secret
- <b>`exist_ok`</b>:  Overwrite existing secret
- <b>`hide`</b>:  Hide secret values from log output

**Note:**

> If `robocorp.log` is available in the environment, the `hide` argument controls if the given values are automatically hidden in the log output.

**Returns:**
Secret container of name, description, and key-value pairs

**Raises:**

- <b>`RobocorpVaultError`</b>:  Error with API request or response payload

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/__init__.py#L72)

```python
create_secret(
    name: str,
    values: dict[str, Any],
    description: str = '',
    exist_ok: bool = False,
    hide: bool = True
) → SecretContainer
```

______________________________________________________________________

# Class `SecretContainer`

Container for a secret with name, description, and multiple key-value pairs.

Avoids logging internal values when possible.

Note that keys are always converted to str internally.

### `__init__`

**Args:**

- <b>`name`</b>:         Name of secret
- <b>`description`</b>:  Human-friendly description for secret
- <b>`values`</b>:       Dictionary of key-value pairs stored in secret

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/_secrets.py#L13)

```python
__init__(name: str, description: str, values: Dict[str, Any])
```

## Properties

- `description`

- `name`

## Methods

______________________________________________________________________

### `update`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/_secrets.py#L32)

```python
update(kvpairs) → None
```

# Exceptions

______________________________________________________________________

## `RobocorpVaultError`

Raised when there's problem with reading from Robocorp Vault.
