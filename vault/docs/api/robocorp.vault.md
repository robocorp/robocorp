<!-- markdownlint-disable -->

<a href="https://github.com/robocorp/robo/tree/master/vault/src/robocorp/vault/__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.vault`





---

<a href="https://github.com/robocorp/robo/tree/master/vault/src/robocorp/vault/__init__.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_secret`

```python
get_secret(name: str, hide: bool = True) → SecretContainer
```

Get a secret with the given name. 



**Args:**

 - <b>`name`</b>:  Name of secret to fetch 
 - <b>`hide`</b>:  Hide secret values from log output 



**Note:**

>If `robocorp.log` is available in the environment, the `hide` argumentcontrols if the given values are automatically hidden in the logoutput.
>

**Returns:**
Secret container of name, description, and key-value pairs 



**Raises:**

 - <b>`RobocorpVaultError`</b>:  Error with API request or response payload. 


---

<a href="https://github.com/robocorp/robo/tree/master/vault/src/robocorp/vault/__init__.py#L47"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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

>If `robocorp.log` is available in the environment, the `hide` argumentcontrols if the given values are automatically hidden in the logoutput.
>

**Raises:**

 - <b>`RobocorpVaultError`</b>:  Error with API request or response payload 


---

<a href="https://github.com/robocorp/robo/tree/master/vault/src/robocorp/vault/__init__.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

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

>If `robocorp.log` is available in the environment, the `hide` argumentcontrols if the given values are automatically hidden in the logoutput.
>

**Returns:**
Secret container of name, description, and key-value pairs 



**Raises:**

 - <b>`RobocorpVaultError`</b>:  Error with API request or response payload 


---

<a href="https://github.com/robocorp/robo/tree/master/vault/src/robocorp/vault/_secrets.py#L5"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `SecretContainer`
Container for a secret with name, description, and multiple key-value pairs. 

Avoids logging internal values when possible. 

Note that keys are always converted to str internally. 

<a href="https://github.com/robocorp/robo/tree/master/vault/src/robocorp/vault/_secrets.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `__init__`

```python
__init__(name: str, description: str, values: Dict[str, Any])
```



**Args:**

 - <b>`name`</b>:         Name of secret 
 - <b>`description`</b>:  Human-friendly description for secret 
 - <b>`values`</b>:       Dictionary of key-value pairs stored in secret 


---

#### <kbd>property</kbd> description





---

#### <kbd>property</kbd> name







---

<a href="https://github.com/robocorp/robo/tree/master/vault/src/robocorp/vault/_secrets.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `update`

```python
update(kvpairs) → None
```






---

<a href="https://github.com/robocorp/robo/tree/master/vault/src/robocorp/vault/_errors.py#L1"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>exception</kbd> `RobocorpVaultError`
Raised when there's problem with reading from Robocorp Vault. 





