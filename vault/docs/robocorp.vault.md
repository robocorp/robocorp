<!-- markdownlint-disable -->

<a href="../../vault/src/robocorp/vault/__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.vault`




**Global Variables**
---------------
- **version_info**

---

<a href="../../vault/src/robocorp/vault/__init__.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_secret`

```python
get_secret(name: str, hide: bool = True) → SecretContainer
```

Get a secret with the given name. 



**Args:**
 
 - <b>`name`</b>:  Name of secret to fetch 
 - <b>`hide`</b>:  Hide secret values from log output 



**Note:**

> If `robocorp.log` is available in the environment, the `hide` argument controls if the given values are automatically hidden in the log output. 
>

**Returns:**
 Secret container of name, description, and key-value pairs 



**Raises:**
 
 - <b>`RobocorpVaultError`</b>:  Error with API request or response payload. 


---

<a href="../../vault/src/robocorp/vault/__init__.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `set_secret`

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
>

**Raises:**
 
 - <b>`RobocorpVaultError`</b>:  Error with API request or response payload 


---

<a href="../../vault/src/robocorp/vault/__init__.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `create_secret`

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
>

**Returns:**
 Secret container of name, description, and key-value pairs 



**Raises:**
 
 - <b>`RobocorpVaultError`</b>:  Error with API request or response payload 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
