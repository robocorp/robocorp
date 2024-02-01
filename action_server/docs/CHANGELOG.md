# Changelog

## 0.0.20 - 2024-01-31

- When importing actions, lint them by default (`--skip-lint` may be used
  to disable linting).
  - `robocorp-actions 0.0.7` is now required.

## 0.0.19 - 2024-01-24

- Instead of defining a `conda.yaml` it's expected that an `action-server.yaml` is defined
  (at this point it's expected that it has the same contents as the `conda.yaml`).

## 0.0.18 - 2024-01-19

- The response from a run now includes an `"X-Action-Server-Run-Id"` header containing the run id.
    - This makes it possible to query more information from `api/runs/{run_id}` after the run finishes.
- Fixed issue where `@action` code would not have logging in place.

## 0.0.17 - 2024-01-19

- By default the minimum number of processes is now 2.
- Console/log output improved.
- Full traceback no longer shown if `robocorp-actions` version does not match the one expected.
- Verify that the `robocorp-actions` version found is 0.0.6 or higher.
    - Required for fixes running `@action` multiple times in the same process.

## 0.0.16 - 2024-01-18

- If a process crashes while in the process pool idle processes it's not reused in a new run.
- When reusing processes, `@setup(scope="session")` is only called once and `@teardown(scope="session")` is no longer called.
    - Requires `robocorp-actions 0.0.6`.
    - Also fixes issue where files containing `@action` would be reimported on each new run when process is reused.

## 0.0.15 - 2024-01-16

- The `--api-key` is now checked in any calls, not just on the connection relative to the `--expose`.
- The Run UI now has a field to specify the `--api-key` to be used in a run.
- Console startup message showing url for action server UI is improved.

## 0.0.14 - 2024-01-16

- It's now possible to specify the server url using the `--server-url` command line parameter.
- A process pool is now available in the action server. The following new arguments are available:
    `--min-processes=<n-processes>`
    `--max-processes=<n-processes>`
    `--reuse-process`
- If the return of an `@action` does not conform to the proper return type a better error message is given.
- Improved keepalive/reconnection on the `--expose` tunnel (ping-pong messages).

## 0.0.13 - 2024-01-14

- Fix main README and update docs.

## 0.0.12 - 2024-01-12

- Auto-trigger brew pipeline after build.

## 0.0.11 - 2024-01-10

- Fixed issue where the actions wouldn't be shown in the UI if the `@action` didn't have any required arguments.

## 0.0.10 - 2024-01-09

- Arguments are passed to the `@action` using `--json-input` command line argument (requires `robocorp-actions 0.0.4`).
  Fixes issue where having long arguments could make the action invocation fail.

## 0.0.9 - 2024-01-08

- Fixed build issue (`rcc` should not be bundled in source release).

## 0.0.8 - 2024-01-08

- Properly depend on node 20.x when doing build.
- Trying to fix build issue (`rcc` should not be bundled in source release).

## 0.0.7 - 2024-01-08

- Make sure that `rcc` is not bundled when doing the source dist (otherwise the linux binary could be wrongly used in mac).
- UI revamp for the action server.
- When an action has default values it can be properly run without passing those as arguments.
- Updated template to start action server project.


## 0.0.6 - 2024-01-05

- `rcc` is now bundled in the action server wheel.
- When the action server is stopped, any subprocess is also killed.
- Pass `@action(is_consequential=True)` to add `x-openai-isConsequential` option to action openapi spec.
- Can be started with `--expose-allow-reuse` to reuse the previously exposed url.


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
