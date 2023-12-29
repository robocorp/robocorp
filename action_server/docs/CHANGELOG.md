# Changelog

## UNRELEASED

- `rcc` is now bundled in the action server wheel.
- When the action server is stopped, any subprocess is also killed.
- Pass `@action(is_consequential=True)` to add `x-openai-isConsequential` option to action openapi spec.

## 0.0.5 - 2023-12-14

- Fixed issues in deployment:
    - `requests` is now a required dep (for --expose to work).
    - _static_contents now properly added by poetry (because it was in .gitignore it was not added to the distribution).
    - "new" command properly checks that RCC is downloaded.
- Running an action with multiple `_` now works from the UI.

## 0.0.4 - 2023-12-13


- `action-server` is not defined as an entry point (so, after installing it,
  an `action-server` executable will be available to execute it instead of having
  to use `python -m robocorp-action-server`).
- Instead of just a text showing the trace header a hyperlink to the trace is also available.
- It's possible to bootstrap a project with `action-server new`.
- Improvements when exposing a server with `--expose`:
    - It's now possible to reuse a previously exposed session with `--expose-session`
    - An API key may be used with `--api-key` for authentication (`--api-key=None` can
      be used to disable authentication).
- By default, when the action server is started with `action-server start`, the
  current directory will be searched for actions and only those actions will be
  served (metadata will be stored in a datadir linked to the current folder).
- For more advanced cases, it's still possible to import actions specifying a
  custom datadir and then start the action server with `--actions-sync=false`
  specifying the proper datadir).
  
i.e.:

```
action-server import --dir=c:/temp=action-package1 --datadir=c:/temp/datadir
action-server import --dir=c:/temp=action-package2 --datadir=c:/temp/datadir
action-server start --actions-sync=false --datadir=c:/temp/datadir
```   

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

