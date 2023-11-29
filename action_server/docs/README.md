# robocorp-action-server

`robocorp-action-server` is a Python framework designed to simplify the deployment
of actions (AI or otherwise).

An `action` in this case is defined as a Python function (which has inputs/outputs
defined) which is served by the `Robocorp Action Server`.

The `Robocorp Action Server` then manages the lifecycle of the action and provides
full traceability of what happened in the action.

## Getting started

It's possible to install the `Robocorp Action Server` with:

`pip install robocorp-action-server`

After it's installed, an `Action Package` must be registered.

An `Action Package` is currently defined as a local folder which contains a 
`conda.yaml` and at least one Python file containing an action entry point 
(a python function marked as `@action` from `robocorp.actions`). 

*See*: https://robocorp.com/docs/setup/installing-python-package-dependencies for
more information on `conda.yaml`. 

*Note*: the `robot.yaml` is not required, but it may be useful to have it to
manually run the actions out of the `Robocorp Action Server`.

To register the `Action Package` it's possible to run:

`python -m robocorp.action_server import --dir=<action-package-dir>`

Then, afterwards it's possible to start the server as:

`python -m robocorp.action_server start`

After it's started, it's possible to access the following urls:

- `/openapi.json`: Provides the openapi spec.
- `/docs`: Provides access to the APIs available in the server and UI to test it.
