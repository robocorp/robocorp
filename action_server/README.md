# robocorp-action-server

[Robocorp Action Server](../readme.md) is a Python framework designed to simplify the deployment
of actions (AI or otherwise).

An `action` in this case is defined as a Python function (which has inputs/outputs
defined), which is served by the `Robocorp Action Server`.

The `Robocorp Action Server` automatically generates an OpenAPI spec for your Python code, enabling different AI/LLM Agents to understand and call your Action. It also manages the Action lifecycle and provides full traceability of what happened during runs.


## 1. Install Action Server
Action Server is available as a stand-alone fully signed executable and via `pip install robocorp-action-server`.
> We recommend the executable to prevent confusion in case you have multiple/crowded Python environments, etc.

#### For macOS

```sh
# Install Robocorp Action Server
brew update
brew install robocorp/tools/action-server 
```

#### For Windows

```sh
# Download Robocorp Action Server
curl -o action-server.exe https://downloads.robocorp.com/action-server/releases/latest/windows64/action-server.exe

# Add to PATH or move to a folder that is in PATH
setx PATH=%PATH%;%CD%
```

#### For Linux

```sh
# Download Robocorp Action Server
curl -o action-server https://downloads.robocorp.com/action-server/releases/latest/linux64/action-server
chmod a+x action-server

# Add to PATH or move to a folder that is in PATH
sudo mv action-server /usr/local/bin/
```

## 2. Run your first Action

```sh
# Bootstrap a new project using this template.
# You'll be prompted for the name of the project (directory):
action-server new

# Start Action Server 
cd my-project
action-server start --expose
```

👉 You should now have an Action Server running locally at: [http://localhost:8080](http://localhost:8080), so open that in your browser and the web UI will guide you further.

👉 Using the `--expose` -flag, you also get a public internet-facing URL (something like "https://twently-cuddly-dinosaurs.robocorp.link") and the related token. These are the details that you need to configure your AI Agent to have access to your Action

## What do you need in your Action Package

An `Action Package` is currently defined as a local folder that contains at least one Python file containing an action entry point (a Python function marked with `@action` -decorator from `robocorp.actions`).

Optionally, you can have a `conda.yaml` for specifying the
Python environment and dependencies for your Action (if a `conda.yaml` is
present, then [RCC](https://github.com/robocorp/rcc/) will be used to 
automatically bootstrap it and keep it updated given the `conda.yaml` contents.


*See*: [More information on `conda.yaml`](https://robocorp.com/docs/setup/installing-python-package-dependencies). 

> A `robot.yaml` used by RCC is not required, but it may be useful to have it to manually run the actions out of the `Robocorp Action Server`.<br/>
We recommend checking out [Robocorp Code](https://robocorp.com/docs/developer-tools/visual-studio-code/extension-features) -extension for VS Code.

### Bootstrapping a new Action

Start new projects with:

`action-server new`

Note: the `action-server` executable should be automatically added to your python installation after `pip install robocorp-action-server`, but if for some reason it wasn't pip-installed, it's also possible to use `python -m robocorp.action_server` instead of `action-server`.

After creating the project, it's possible to serve the actions under the
current directory with:

`action-server start`

For example: When running `action-server start`, the action server will scan for existing actions under the current directory, and it'll start serving those.

After it's started, it's possible to access the following URLs:

- `/index.html`: UI for the Action Server.
- `/openapi.json`: Provides the openapi spec for the action server.
- `/docs`: Provides access to the APIs available in the server and a UI to test it.


## API Reference

Information on specific functions or classes: [robocorp.action-server](https://github.com/robocorp/robocorp/blob/master/action_server/docs/api/README.md)

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/action_server/docs/CHANGELOG.md).
