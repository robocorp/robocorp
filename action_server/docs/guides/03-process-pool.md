Running actions
===================

The action server has a few command line parameters when it's started which define how
actions will be run and whether actions must be run isolated from other actions.


Reuse process
================

The most important flag here is `--reuse-process`. When this flag is activated, 
the action server will invoke the same `@action` multiple times, utilizing 
the same process where the `@action` was previously executed.

If `--reuse-process` is not passed, a new process will be created to run the action
and each new invocation will run in a completely clean environment.


Notes on process reusal:
=========================

It's usually faster to run with `--reuse-process`
as after the action runs once, all modules are already imported and the global
state is reused (so, subsequent calls to the action will have the same
global variables in place).

Keep in mind that some environment variables may be changed across calls 
to an `@action` (for instance to update where the results should be written).
In such cases, those should not be stored in a global variable.


Process pool
==============

The action server can execute processes using a process pool (by providing the
`--min-processes` and `--max-processes` command line arguments).

In general, if `--reuse-process` is set and more than one process is available,
the action server may redirect a new request to any of the existing processes
(as long as the environment is compatible), so, for instance, if there are
three different `@action`s in the same package, the action server can forward 
a request to any of the existing processes.

This implies that unless `--min-processes` and `--max-processes` are both 
set to `1` and `--reuse-process` is enabled, global state that needs to 
persist for handling session information should be stored externally 
(e.g., in a sqlite database or another external service/location for 
storing user-session information).

