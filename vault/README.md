# Robocorp Control Room Vault API library

`robocorp-vault` is a library which provides read and write access to the
`Vault` at `Robocorp Control Room`.


## Usage


```python    
from robocorp import vault

def reading_secrets():
    secrets_container = vault.get_secret('secret_name')
    print(f"Username: {secrets_container['username']}")
    print(f"My secrets: {secrets_container}")

def modifying_secrets():
    secret = vault.get_secret("swaglabs")
    secret["username"] = "nobody"
    vault.set_secret(secret)
```