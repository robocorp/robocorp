## Secrets

*Important*: Requires `robocorp-actions 0.2.0` onwards to work.

### Receiving a Secret

To receive secrets using actions, it's possible to add a parameter with a 
'Secret' type so that it's automatically received by the action.

i.e.:

```
from robocorp.actions import action, Secret

@action
def my_action(my_secret: Secret):
    login(my_secret.value)
```

### Passing Secrets (Dev mode)

In development mode a secret can be passed by using the `input.json`

i.e.: in the case above a `my_secret` entry in the json will be automatically
used as the `my_secret.value`.

Example `input.json`:

```json
{
    "my_secret": "secret-value"
}
```

### Passing Secrets (Production mode)

In production secrets should be passed in the `X-Action-Server` header.

The expected format of that header is a base64(JSON.stringify(content))
where the content is a json object such as:

```
{
    "secrets": {
        "secret-name": "secret-value"
    }
}
```

In python code it'd be something as:

```python
payload = {
    'secrets': {'secret-name': 'secret-value'}
}
x_action_server_header = base64.b64encode(
    json.dumps(
        payload
    ).encode("utf-8")
).decode("ascii")
``` 

Note: the `X-Action-Server` header can also be passed encrypted with a
key shared with the action server in the environment variables.

In that case the `X-Action-Server` header contents should be something as:

```
base64({
    "cipher": base64(encrypted_data(JSON.stringify(content))),
    "algorithm": "aes256-cdc",
    "iv": base64(nonce),
})
```

In python code it'd be something as:

```python

payload = {
    'secrets': {'secret-name': 'secret-value'}
}
data: bytes = json.dumps(payload).encode("utf-8")

# def encrypt(...) implementation can be created using the cryptography library.

encrypted_data = encrypt(key, nonce, data)

action_server_context = {
    "cipher": base64.b64encode(encrypted_data).decode("ascii"),
    "algorithm": "aes256-cdc",
    "iv": base64.b64encode(nonce).decode("ascii"),
}

x_action_server_header: str = base64.b64encode(
    json.dumps(action_server_context).encode("utf-8")
).decode("ascii")
```

The actual `key` used in the encryption should be set in `ACTION_SERVER_DECRYPT_KEYS`
in the environment variables such that it's a json with the keys in base64.

In python code:

```python
ACTION_SERVER_DECRYPT_KEYS=json.dumps(
    [base64.b64encode(k).decode("ascii") for k in keys]
)
```

Note: all the keys will be checked in order and the caller may use any of the 
keys set to encrypt the data.