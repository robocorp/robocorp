# Changelog

## 0.0.3 - 2023-12-08

- UI now uses websockets to provide updates on runs in real-time.
- The static assets are bundled into the application so that the distributed version has access to it.
- It's possible to `--expose` the server on the public web using a 'robocorp.link'.
- A text showing the trace header is now available in the logs.
- Other UI improvements.

## 0.0.2 - 2023-12-05

- Still pre-alpha.
- Internal DB migration available.
- Initial UI available.
    - Allows running from the UI.
    - Shows action packages, actions and runs.
    - The console and log.html can be seen.
    - API to expose the server to the web.
    - Known issue: requests for runs and actions are cached and a full page request is needed to get new information.

## 0.0.1 - 2023-11-29

- First release (pre-alpha).
- Can import actions in the backend and run using API

