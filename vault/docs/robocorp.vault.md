<!-- markdownlint-disable -->

<a href="..\..\vault\src\robocorp\vault\__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.vault`
`robocorp.vault` is a library for interacting with secrets stored in the ``Robocorp Control Room Vault``. 

Uses ``Robocorp Control Room Vault`` (by default) or file-based secrets, which can be taken into use by setting some environment variables. 

Robocorp Vault relies on environment variables, which are normally set automatically by the Robocorp Work Agent or Assistant when a run is initialized by the Robocorp Control Room. When developing robots locally in VSCode, you can use the `Robocorp Code Extension`_ to set these variables automatically as well. 

Alternatively, you may set these environment variable manually using `rcc`_ or directly in some other fashion. The specific variables which must exist are: 


- ``RC_API_SECRET_HOST``: URL to Robocorp Vault API 
- ``RC_API_SECRET_TOKEN``: API Token for Robocorp Vault API 
- ``RC_WORKSPACE_ID``: Control Room Workspace ID 

.. _Robocorp Control Room Vault: https://robocorp.com/docs/development-guide/variables-and-secrets/vault .. _Robocorp Code Extension: https://robocorp.com/docs/developer-tools/visual-studio-code/extension-features#connecting-to-control-room-vault .. _rcc: https://robocorp.com/docs/rcc/workflow 

File-based secrets can be set by defining two environment variables. 


- ``RC_VAULT_SECRET_MANAGER``: FileSecrets 
- ``RC_VAULT_SECRET_FILE``: Absolute path to the secrets database file 

Example content of local secrets file: 

```json
{
     "swaglabs": {
         "username": "standard_user",
         "password": "secret_sauce"
     }
}
``` 



OR 

```yaml

swaglabs:
     username: standard_user
     password: secret_sauce
``` 



**Example:**
 

```python    
from robocorp import vault

def reading_secrets():
     secrets_container = vault.get_secret('swaglabs')
     print(f"My secrets: {secrets_container}")
     
def modifying_secrets():
     secret = vault.get_secret("swaglabs")
     secret["username"] = "nobody"
     vault.set_secret(secret)
``` 

**Global Variables**
---------------
- **version_info**

---

<a href="..\..\vault\src\robocorp\vault\__init__.py#L82"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `get_secret`

```python
get_secret(secret_name: str) → SecretContainer
```

Get secret defined with given name. 



**Args:**
 
 - <b>`secret_name`</b>:  Name of secret to fetch. 



**Note:**

> The returned secret is not cached, so, calling this function again may do a new network roundtrip. 
>

**Returns:**
 The container for the secret (which has key-value pairs). 



**Raises:**
 
 - <b>`RobocorpVaultError`</b>:  Error with API request or response payload. 


---

<a href="..\..\vault\src\robocorp\vault\__init__.py#L117"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `set_secret`

```python
set_secret(secret: SecretContainer) → None
```

Overwrite an existing secret with new values. 



**Note:**

> Only allows modifying existing secrets, and replaces all values contained within it. 
>

**Args:**
 
 - <b>`secret`</b>:  the secret object which was mutated. 




---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
