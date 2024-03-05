# Whitelisting actions to be run

There are 2 situations where one can whitelist the actions which should
be used, at import and at server start time.

This can be specified in the `--whitelist` command line parameter.

## Whitelist argument spec

- The format of the whitelist is flexible so that it accepts the format
  accepted by [fnmatch](https://docs.python.org/3/library/fnmatch.html).

- The package name can potentially be matched too (if `/` is added the package
  name is matched, otherwise just the action name is matched).

- It's possible to specify multiple actions by separating them with a comma.

- `-` and `_` may be used interchangeably. 

## Examples

`--whitelist "action-1,action_2"`

`--whitelist "package1/action*1,package2/action*2"`

`--whitelist "*foo/sheet,*bar/sheet"`

`--whitelist "*foo/*"`

### Importing actions

When actions are imported, it's possible to whitelist which actions should
actually be imported.

Example:

```
action-server import --datadir=<path to datadir> --whitelist my_action1,my_action2
action-server start --actions-sync=false --datadir=<path to datadir>
```


### Serving actions

When actions are served, it's possible to whitelist which actions should
actually be available to run.

Example:

```
action-server start --datadir=<path to datadir> --whitelist my_action1,my_action2
```
