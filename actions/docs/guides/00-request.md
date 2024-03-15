## Getting request data (such as headers) in Actions

Starting with `robocorp-actions 0.1.0`, it's possible to collect data from the
received request by creating a `request: Request` argument.

The data currently available in the request is:

- `headers`: contains all the headers received except cookies.
- `cookies`: contains all the cookies received.

Note that the access to headers and cookies is case-insensitive.

### Example:

```
from robocorp.actions import action, Request

@action
def my_action(request: Request):
    header: Optional[str] = request.headers.get('X-custom-header')
    cookie: Optional[str] = request.cookies.get('X-custom-cookie')

```

Note: for testing it's possible to set the `request` (with its `headers` and `cookies`)
using the `--json-input`.

In a production environment it'll be provided by the Action Server.