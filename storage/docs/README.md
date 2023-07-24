# robocorp-storage

`robocorp-storage` is a library which provides read and write access to the
*Asset Storage* in Robocorp Control Room.

## Getting started

```python
from robocorp import storage

def store_email():
    storage.set_text("cosmin", "cosmin@robocorp.com")
    print("E-mail:", storage.get_text("cosmin"))
    storage.delete_asset("cosmin")
```

## Guides

- [Handling different asset types](./guides/asset-types.md)

Further user guides and tutorials can be found in [Robocorp Docs](https://robocorp.com/docs).

## API Reference

Information on specific functions or classes: [robocorp.storage](./api/robocorp.storage.md)

## Changelog

A list of releases and corresponding changes can be found in the [changelog](./CHANGELOG.md).
