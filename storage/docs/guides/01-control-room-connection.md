# Control Room connection settings

The library talks to the Control Room asset storage API over HTTPS. The
defaults suit most robots, and the environment variables below change them when
needed. The timeout and idle limit are read once, when the library is imported,
so set them before the robot starts.

| Variable | Default | Effect |
|---|---|---|
| `RC_API_REQUEST_TIMEOUT` | `60` | Seconds to wait for a connection or a response before the request fails and is retried. |
| `RC_API_CONNECTION_MAX_IDLE` | `30` | Seconds a connection can stay unused and still be reused. |
| `RC_DISABLE_SSL` | not set | Any non-empty value turns off TLS certificate verification. |

## Connection reuse

Each asset operation takes several HTTP requests. Setting an asset looks it up
or creates it, creates an upload, and for large content sends it with a
separate request. By default it then waits for the upload to finish by checking
its status every 0.5 seconds. The library keeps its connections open between
these requests, so each one doesn't pay for a new TCP and TLS handshake. This
matters most when the robot runs far from Control Room, where a new connection
costs several network round trips.

A firewall or NAT on the network path can forget an idle connection without
telling either side. A request sent on such a connection gets no answer and
waits for the full request timeout. To avoid this, a connection that has been
unused for longer than `RC_API_CONNECTION_MAX_IDLE` is closed, and the next
request opens a new one. This isn't a timer: the check happens only when the
next request is sent.

For example, the status checks while an upload finishes are half a second
apart, so they all reuse one connection. A robot that sets an asset, works for a
few minutes and then reads another opens a new connection for that read, which
costs one handshake.

You can raise the limit, for example `RC_API_CONNECTION_MAX_IDLE=300`, if you
know that nothing on your network path drops idle connections within that time.
Set it to `0` to open a new connection for every request, as versions before
connection reuse did.

## Request timeout and retries

A request that fails with a server error, a rate limit (HTTP 429), a connection
error or a timeout is retried up to 4 times, with a random back-off of up to 5
seconds between attempts. Responses with status 400, 401, 403, 404 or 409 are
not retried, since repeating the same request wouldn't help.

`RC_API_REQUEST_TIMEOUT` applies to connecting and to each wait for response
data, not to the request as a whole.

## Disabling certificate verification

`RC_DISABLE_SSL` turns off TLS certificate verification for every request the
library makes, including asset content downloads and uploads. Use it only for
testing, for example behind a proxy that intercepts TLS with a certificate the
robot doesn't trust. In that case, prefer pointing `REQUESTS_CA_BUNDLE` at the
proxy's CA certificate instead.
