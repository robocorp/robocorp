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

An `Action Package` is currently defined as a local folder which contains
at least one Python file containing an action entry point (a python 
function marked as `@action` from `robocorp.actions`).

Optionally it may also contain a `conda.yaml` for specifying the
environment in which the actions should be run (if a `conda.yaml` is
present then [RCC](https://github.com/robocorp/rcc/) will be used to 
automatically bootstrap it and keep it updated given the `conda.yaml` contents.

*See*: https://robocorp.com/docs/setup/installing-python-package-dependencies for
more information on `conda.yaml`. 

*Note*: a `robot.yaml` used by RCC is not required, but it may be useful to have it to
manually run the actions out of the `Robocorp Action Server`.

### Bootstraping

The first project may be bootstrapped with:

`action-server new`

Note: the `action-server` executable should be automatically added to your
python installation after `pip install robocorp-action-server`, but if for some
reason it wasn't pip-installed, it's also possible to use `python -m robocorp.action_server`
instead of `action-server`.

After creating the project, it's possible to serve the actions under the
current directory with:

`action-server start`

i.e.: When running `action-server start` the action server will scan for existing
actions under the current directory and it'll start serving those.

After it's started, it's possible to access the following urls:

- `/index.html`: Page which allows interacting with the action server.
- `/openapi.json`: Provides the openapi spec for the action server.
- `/docs`: Provides access to the APIs available in the server and an UI to test it.


## API Reference

Information on specific functions or classes: [robocorp.action-server](https://github.com/robocorp/robocorp/blob/master/action_server/docs/api/README.md)

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/action_server/docs/CHANGELOG.md).
