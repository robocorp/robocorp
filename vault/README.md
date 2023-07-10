# Robocorp Control Room Vault API library

`robocorp-vault` is a library which provides read and write access to the
`Vault` at `Robocorp Control Room`.

## Usage

```python    
from robocorp import vault
from robocorp import log 

def reading_secrets():
    secrets_container = vault.get_secret('secret_name')
    # Shows secret keys available:
    print(f"My secrets: {secrets_container}")
    # Note: actually prints the secret value below.
    print(f"Username: {secrets_container['username']}")

def modifying_secrets():
    secret = vault.get_secret("swaglabs")
    with log.suppress_variables():
        secret_value = collect_new_secret_value()
        secret["username"] = secret_value
        vault.set_secret(secret)
```

Note that values set or gotten from the vault will be automatically
hidden from `robocorp.log` logs (if `robocorp.log` is available
in the environment), but care needs to be taken when setting it
so that secrets don't become exposed before being set into the vault.

i.e.: When setting values into the vault, if such values are sensitive,
use `with robocorp.log.suppress_variables()` so that such value doesn't
become logged before it's received by the vault.
