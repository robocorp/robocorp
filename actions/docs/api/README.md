<!-- markdownlint-disable -->

# API Overview

## Modules

- [`robocorp.actions`](./robocorp.actions.md#module-robocorpactions)
- [`robocorp.actions.cli`](./robocorp.actions.cli.md#module-robocorpactionscli)

## Classes

- [`_protocols.IAction`](./robocorp.actions._protocols.md#class-iaction)
- [`_request.Request`](./robocorp.actions._request.md#class-request): Contains the information exposed in a request (such as headers and cookies).
- [`_protocols.Status`](./robocorp.tasks._protocols.md#class-status): Task state

## Functions

- [`actions.action`](./robocorp.actions.md#function-action): Decorator for actions (entry points) which can be executed by `robocorp.actions`.
- [`actions.action_cache`](./robocorp.actions.md#function-action_cache): Provides decorator which caches return and clears it automatically when the
- [`actions.get_current_action`](./robocorp.actions.md#function-get_current_action): Provides the action which is being currently run or None if not currently
- [`actions.get_output_dir`](./robocorp.actions.md#function-get_output_dir): Provide the output directory being used for the run or None if there's no
- [`actions.session_cache`](./robocorp.actions.md#function-session_cache): Provides decorator which caches return and clears automatically when all
- [`_fixtures.setup`](./robocorp.actions._fixtures.md#function-setup): Run code before any actions start, or before each separate action.
- [`_fixtures.teardown`](./robocorp.actions._fixtures.md#function-teardown): Run code after actions have been run, or after each separate action.
- [`cli.main`](./robocorp.actions.cli.md#function-main): Entry point for running actions from robocorp-actions.
