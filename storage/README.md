# robocorp-storage

`robocorp-storage` is a library which provides read and write access to the [Asset Storage](https://robocorp.com/docs/control-room/asset-storage) in Robocorp Control Room.

## Getting started

```python
from robocorp import storage

def store_email():
    storage.set_text("cosmin", "cosmin@robocorp.com")
    print("E-mail:", storage.get_text("cosmin"))
    storage.delete_asset("cosmin")
```

## Guides

- [Handling different asset types](https://github.com/robocorp/robocorp/blob/master/storage/docs/guides/00-asset-types.md)

## API Reference

Explore our [API](https://github.com/robocorp/robocorp/blob/master/storage/docs/api/README.md) for extensive documentation.

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/storage/docs/CHANGELOG.md).
