# Robocorp Control Room Asset Storage API library

`robocorp-storage` is a library which provides read and write access to the
*Asset Storage* in Robocorp **Control Room**.


## Usage

```python
from robocorp import storage

def store_email():
    storage.set_asset("cosmin", "cosmin@robocorp.com")
    print("E-mail:", storage.get_asset("cosmin"))
    storage.delete_asset("cosmin")
```
