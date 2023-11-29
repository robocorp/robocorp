Robocorp Actions Server
=========================

Internal structure:

The server works with a datadir (which may be specified in the command line).

Below that datadir, the following structure will be used:

`/server.db`:
    This is the (sqlite) database used to hold information on the server.

See: `@dataclasses` on [`_models.py:36`](https://github.com/robocorp/robo-action-server/blob/master/action_server/src/robocorp/action_server/_models.py)
for the model information stored in sqlite.

`/artifacts`

    This is the directory where artifacts from the runs are stored.

`/artifacts/{run_id}`: the output contents of the run are stored here.
    `/inputs.json`: the inputs as json.
    `/result.json`: the result as json.
    `/output.txt`: console output.

`/packages`

    Directory containing the packages

`/packages/{package_id}`

    The content of each package is stored here.

