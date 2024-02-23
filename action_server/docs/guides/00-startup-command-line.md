# Serving Actions with the Action Server

The action server's main purpose is managing the lifecycle of actions in
an action package.

There are a number of customizations available which make it flexible to
work and manage which actions should be executed. The guide shows a few
of these use-cases below.

## Serving actions from the current directory

The simplest case is just starting the action server at a given folder
with:

```
action-server start
```

In this case, the action server will search recursively for all the Actions
marked as `@action` in files named as `*action*.py` and then it'll start
serving such actions. Any `@action` which 
is no longer found from a previous run will be disabled.

All the settings and data related to this run will be stored a folder
located in a directory in `~/robocorp/.action_server` (or
`%LOCALAPPDATA%/robocorp/.action_server` in windows) which is automatically
computed based on the current directory location.

It's possible to customize the directory by using the `--datadir` flag.

Example:
 
```
action-server start --datadir=<path to datadir>
```

## Serving actions from multiple directories

In this case, instead of just using `action-server start`, one needs to
import the actions saving the settings to a given datadir and then 
start the server pointing to that datadir asking the `action-server` 
not to synchronize the actions again when starting.

Example:
 
```
action-server import --dir=<path to action-package 1> --datadir=<path to datadir>
action-server import --dir=<path to action-package 2> --datadir=<path to datadir>
action-server start --actions-sync=false --datadir=<path to datadir>
```
