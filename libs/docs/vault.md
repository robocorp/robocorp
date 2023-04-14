<!-- markdownlint-disable -->

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `vault`






---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L28"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RobocorpVaultError`
Raised when there's problem with reading from Robocorp Vault. 





---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L32"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Secret`
Container for a secret with name, description, and multiple key-value pairs. 

Immutable and avoids logging internal values when possible. 



**Args:**
 
 - <b>`name`</b>:         Name of secret 
 - <b>`description`</b>:  Human-friendly description for secret 
 - <b>`values`</b>:       Dictionary of key-value pairs stored in secret 

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L44"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(name, description, values)
```






---

#### <kbd>property</kbd> description





---

#### <kbd>property</kbd> name







---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L57"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `update`

```python
update(kvpairs)
```






---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L81"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `BaseSecretManager`
Abstract class for secrets management. 

Should be used as a base-class for any adapter implementation. 




---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_secret`

```python
get_secret(secret_name)
```

Return ``Secret`` object with given name. 

---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_secret`

```python
set_secret(secret: Secret)
```

Set a secret with a new value. 


---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L97"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `FileSecrets`
Adapter for secrets stored in a database file. 

Supports only plaintext secrets, and should be used mainly for debugging. 

The path to the secrets file can be set with the environment variable ``RPA_SECRET_FILE``, or as an argument to the library. 

The format of the secrets file should be one of the following: 

.. code-block:: JSON 

 {  "name1": {  "key1": "value1",  "key2": "value2"  },  "name2": {  "key1": "value1"  }  } 

OR 

.. code-block:: YAML 

 name1:  key1: value1  key2: value2  name2:  key1: value1 

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(secret_file='secrets.json')
```








---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L179"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_secret`

```python
get_secret(secret_name) → Secret
```

Get secret defined with given name from file. 



**Args:**
 
 - <b>`secret_name`</b>:  Name of secret to fetch 

**Returns:**
 
 - <b>`Secret`</b>:  Secret object 



**Raises:**
 
 - <b>`KeyError`</b>:  No secret with given name 

---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L155"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `load`

```python
load()
```

Load secrets file. 

---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L169"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save`

```python
save()
```

Save the secrets content to disk. 

---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L197"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_secret`

```python
set_secret(secret: Secret) → None
```

Set the secret value in the local Vault with the given ``Secret`` object. 



**Args:**
 
 - <b>`secret`</b>:  A ``Secret`` object. 



**Raises:**
 
 - <b>`IOError`</b>:  Writing the local vault failed. 
 - <b>`ValueError`</b>:  Writing the local vault failed. 


---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L212"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RobocorpVault`
Adapter for secrets stored in Robocorp Vault. 

The following environment variables should exist: 


- RC_API_SECRET_HOST:   URL to Robocorp Secrets API 
- RC_API_SECRET_TOKEN:  API token with access to Robocorp Secrets API 
- RC_WORKSPACE_ID:      Robocorp Workspace ID 

If the robot run is started from the Robocorp Control Room these environment variables will be configured automatically. 

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L228"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(*args, **kwargs)
```






---

#### <kbd>property</kbd> headers

Default request headers. 

---

#### <kbd>property</kbd> params

Default request parameters. 



---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L281"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_public_key_url`

```python
create_public_key_url()
```

Create a URL for encryption public key. 

---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L275"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_secret_url`

```python
create_secret_url(name)
```

Create a URL for a specific secret. 

---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L393"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_publickey`

```python
get_publickey() → bytes
```

Get the public key for AES encryption with the existing token. 

---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L292"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_secret`

```python
get_secret(secret_name) → Secret
```

Get secret defined with given name from Robocorp Vault. 



**Args:**
 
 - <b>`secret_name`</b>:  Name of secret to fetch 

**Returns:**
 
 - <b>`Secret`</b>:  Secret object 



**Raises:**
 
 - <b>`RobocorpVaultError`</b>:  Error with API request or response payload 

---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L353"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_secret`

```python
set_secret(secret: Secret) → None
```

Set the secret value in the Vault. 



**Note:**

> The secret possibly consists of multiple key-value pairs, which will all be overwritten with the values given here. So don't try to update only one item of the secret, update all of them. 
>

**Args:**
 
 - <b>`secret`</b>:  A ``Secret`` object 


---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L458"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Vault`
`Vault` is a library for interacting with secrets stored in the ``Robocorp Control Room Vault``. 

Uses ``Robocorp Control Room Vault`` (by default) or file-based secrets, which can be taken into use by setting some environment variables. 

Robocorp Vault relies on environment variables, which are normally set automatically by the Robocorp Work Agent or Assistant when a run is initialized by the Robocorp Control Room. When developing robots locally in VSCode, you can use the `Robocorp Code Extension`_ to set these variables automatically as well. 

Alternatively, you may set these environment variable manually using `rcc`_ or directly in some other fashion. The specific variables which must exist are: 


- ``RC_API_SECRET_HOST``: URL to Robocorp Vault API 
- ``RC_API_SECRET_TOKEN``: API Token for Robocorp Vault API 
- ``RC_WORKSPACE_ID``: Control Room Workspace ID 

.. _Robocorp Control Room Vault: https://robocorp.com/docs/development-guide/variables-and-secrets/vault .. _Robocorp Code Extension: https://robocorp.com/docs/developer-tools/visual-studio-code/extension-features#connecting-to-control-room-vault .. _rcc: https://robocorp.com/docs/rcc/workflow 

File-based secrets can be set by defining two environment variables. 


- ``RPA_SECRET_MANAGER``: RPA.Robocorp.Vault.FileSecrets 
- ``RPA_SECRET_FILE``: Absolute path to the secrets database file 

Example content of local secrets file: 

.. code-block:: json 

 {  "swaglabs": {  "username": "standard_user",  "password": "secret_sauce"  }  } 

OR 

.. code-block:: YAML 

 swaglabs:  username: standard_user  password: secret_sauce 



**Example:**
  .. code-block:: python 

 from RPA.Robocorp.Vault import Vault 

 VAULT = Vault() 

 def reading_secrets():  print(f"My secrets: {VAULT.get_secret('swaglabs')}") 

 def modifying_secrets():  secret = VAULT.get_secret("swaglabs")  secret["username"] = "nobody"  VAULT.set_secret(secret) 

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L523"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(*args, **kwargs)
```

The selected adapter can be set with the environment variable. 

Use the environment variable ``RPA_SECRET_MANAGER``, or the argument ``default_adapter``. Defaults to Robocorp Vault if not defined. 

All other library arguments are passed to the adapter. 



**Args:**
 
 - <b>`default_adapter`</b>:  Override default secret adapter 


---

#### <kbd>property</kbd> adapter







---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L564"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_secret`

```python
get_secret(secret_name: str) → Secret
```

Read a secret from the configured source, e.g. Robocorp Vault. 



**Args:**
 
 - <b>`secret_name`</b>:  Name of secret 



**Returns:**
 
 - <b>`Secret`</b>:  ``Secret`` object 

---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\robocorp\src\robo\libs\robocorp\vault.py#L576"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_secret`

```python
set_secret(secret: Secret) → None
```

Overwrite an existing secret with new values. 



**Note:**

> Only allows modifying existing secrets, and replaces all values contained within it. 
>

**Args:**
 
 - <b>`secret`</b>:  Secret as a ``Secret`` object, from e.g. ``Get Secret`` 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
