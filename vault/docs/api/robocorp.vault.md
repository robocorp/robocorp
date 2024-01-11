<!-- markdownlint-disable -->

# module `robocorp.vault`

**Source:** [`__init__.py:0`](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/__init__.py#L0)

______________________________________________________________________

## function `get_secret`

**Source:** [`__init__.py:19`](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/__init__.py#L19)

```python
get_secret(name: str, hide: bool = True) → SecretContainer
```

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

______________________________________________________________________

## function `set_secret`

**Source:** [`__init__.py:47`](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/__init__.py#L47)

```python
set_secret(secret: SecretContainer, hide: bool = True) → None
```

Set a secret value using an existing container.

**Note:** If the secret already exists, all contents are replaced.

**Args:**

- <b>`secret`</b>:  Secret container, created manually or returned by `get_secret`
- <b>`hide`</b>:  Hide secret values from log output

**Note:**

> If `robocorp.log` is available in the environment, the `hide` argument controls if the given values are automatically hidden in the log output.

**Raises:**

- <b>`RobocorpVaultError`</b>:  Error with API request or response payload

______________________________________________________________________

## function `create_secret`

**Source:** [`__init__.py:72`](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/__init__.py#L72)

```python
create_secret(
    name: str,
    values: dict[str, Any],
    description: str = '',
    exist_ok: bool = False,
    hide: bool = True
) → SecretContainer
```

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

______________________________________________________________________

## class `SecretContainer`

**Source:** [`_secrets.py:5`](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/_secrets.py#L5)

Container for a secret with name, description, and multiple key-value pairs.

Avoids logging internal values when possible.

Note that keys are always converted to str internally.

### method `__init__`

**Source:** [`_secrets.py:13`](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/_secrets.py#L13)

```python
__init__(name: str, description: str, values: Dict[str, Any])
```

**Args:**

- <b>`name`</b>:         Name of secret
- <b>`description`</b>:  Human-friendly description for secret
- <b>`values`</b>:       Dictionary of key-value pairs stored in secret

#### property `description`

#### property `name`

______________________________________________________________________

### method `update`

**Source:** [`_secrets.py:32`](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/_secrets.py#L32)

```python
update(kvpairs) → None
```

______________________________________________________________________

## exception `RobocorpVaultError`

**Source:** [`_errors.py:1`](https://github.com/robocorp/robocorp/tree/master/vault/src/robocorp/vault/_errors.py#L1)

Raised when there's problem with reading from Robocorp Vault.
