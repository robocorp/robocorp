# Handling different asset types

On the most basic level, the Asset Storage feature stores binary data that
is associated with a name and information about the content type.

The Control Room UI has built several abstractions on top of it, such
as directly uploading text or JSON. These different asset types can also
be directly read and created from within the library.

## Text

The `text` methods can be used for directly reading and writing plaintext
assets, with the content type `text/plain`.

```python
from robocorp import storage
from robocorp.tasks import task

@task
def handle_text():
    content = storage.get_text("some-text-asset")
    print(f"Stored text content: {content}")

    storage.set_text("another-text-asset", "This is a Python string stored directly")
```

## JSON

The `json` methods can be used to read and write any data that can be
serialized into JSON. Values read as JSON are automatically deserialized
into Python objects. They have the content type `application/json`.

```python
from robocorp import storage
from robocorp.tasks import task

@task
def handle_json():
    value = storage.get_json("some-json-asset")
    print(f"Stored JSON content: {value}")

    storage.set_json("another-json-asset", {
        "key": "value",
        "another-key": {
            "nested-key": "nested-value",
        },
    })
```

## Files

The `file` methods are an abstraction that help with working data that
exist on the file system instead of within Python code. The content type
can be defined manually, but the library tries to guess it automatically
based on the file's suffix.

```python
from robocorp import storage
from robocorp.tasks import task

@task
def handle_file():
    path = storage.get_file("some-file-asset")
    print(f"Stored file path: {path}")

    storage.set_file("another-file-asset", "filename.txt")
```

## Bytes

The lowest level API, for handling arbitrary binary data and a manually
defined content type:

```python
from robocorp import storage
from robocorp.tasks import task

@task
def handle_bytes():
    data = storage.get_bytes("some-bytes-asset")
    print(f"Stored bytes data: {data}")

    storage.set_bytes(
        "another-bytes-asset",
        b"\x00\x00\x00",
        content_type="application/octet-stream",
    )
```
