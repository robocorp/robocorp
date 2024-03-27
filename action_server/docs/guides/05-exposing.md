## Exposing a local action server

To expose a local running action server for public access, it's possible
to use `action-server start --expose`.

By doing so, the `action-server` will automatically connect to a
server and you'll get a public reference to it on the `robocorp.link` domain
(for instance `https://twently-cuddly-dinosaurs.robocorp.link`).

Note: if the server is stopped and restarted, it'll ask to reconnect to
the same server afterwards as url/access secret is stored in the datadir.
If you say `No`, a new url/access secret will be generated and the old
one will be lost, so, it may be interesting to backup the `expose_session.json`
from your datadir if you plan to keep using the same url later on (the datadir is 
printed in the console whenever you start your action server). 

### Authentication

Currently the Action Server supports a basic authentication scheme using 
an API key with "Bearer" authentication.

To set it up, it's possible to pass `--api-key=<api key>` in the
to the `action-server start`.

Note that if `--api-key` is not passed along with `--expose`, an
api key will be automatically generated and saved in your `datadir/.api_key`.
Consider backing it up if you want to keep using the same api key.


### Calling server with API key enabled

If the `--api-key` was passed (or if this was an exposed server which
had the api automatcially generated), to call any method from its API, 
a header such as:

`"Authorization": "Bearer <api-key>"`

must be passed in all requests (excluding `/openapi.json`).
