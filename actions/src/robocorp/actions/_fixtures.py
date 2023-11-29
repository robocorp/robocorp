from typing import Callable, Literal, TypeVar, Union, overload

from ._protocols import IActionCallback, IActionsCallback

T = TypeVar("T")
Decorator = Callable[[T], T]


@overload
def setup(func: IActionCallback) -> IActionCallback:
    ...


@overload
def setup(*, scope: Literal["action"] = "action") -> Decorator[IActionCallback]:
    ...


@overload
def setup(*, scope: Literal["session"]) -> Decorator[IActionsCallback]:
    ...


def setup(
    *args, **kwargs
) -> Union[IActionCallback, Decorator[IActionCallback], Decorator[IActionsCallback]]:
    """Run code before any actions start, or before each separate action.

    Receives as an argument the action or actions that will be run.

    Can be used as a decorator without arguments:

    ```python
    from robocorp.actions import setup

    @setup
    def my_fixture(action):
        print(f"Before action: {action.name}")
    ```

    Alternatively, can be called with a `scope` argument to decide when
    the fixture is run:

    ```python
    from robocorp.actions import setup

    @setup(scope="action")
    def before_each(action):
        print(f"Running action '{action.name}'")

    @setup(scope="session")
    def before_all(actions):
        print(f"Running {len(actions)} action(s)")
    ```

    By default, runs setups in `action` scope.

    The `setup` fixture also allows running code after the execution,
    if it `yield`s the execution to the action(s):

    ```python
    import time
    from robocorp.actions import setup

    @setup
    def measure_time(action):
        start = time.time()
        yield  # Action executes here
        duration = time.time() - start
        print(f"Action took {duration} seconds")

    @action
    def my_long_action():
        ...
    ```

    **Note:** If fixtures are defined in another file, they need to be imported
     in the main actions file to be taken into use
    """
    from robocorp.tasks import setup as _setup

    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        return _setup(*args, **kwargs)

    scope = kwargs.pop("scope", "action")
    if scope == "action":
        scope = "task"

    elif scope == "session":
        pass

    else:
        raise ValueError(f"Unknown scope '{scope}', expected 'action' or 'session'")

    kwargs["scope"] = scope
    return _setup(*args, **kwargs)


@overload
def teardown(func: IActionCallback) -> IActionCallback:
    ...


@overload
def teardown(*, scope: Literal["action"] = "action") -> Decorator[IActionCallback]:
    ...


@overload
def teardown(*, scope: Literal["session"]) -> Decorator[IActionsCallback]:
    ...


def teardown(
    *args, **kwargs
) -> Union[IActionCallback, Decorator[IActionCallback], Decorator[IActionsCallback]]:
    """Run code after actions have been run, or after each separate action.

    Receives as an argument the action or actions that were executed, which
    contain (among other things) the resulting status and possible error message.

    Can be used as a decorator without arguments:

    ```python
    from robocorp.actions import teardown

    @teardown
    def my_fixture(action):
        print(f"After action: {action.name})
    ```

    Alternatively, can be called with a `scope` argument to decide when
    the fixture is run:

    ```python
    from robocorp.actions import teardown

    @teardown(scope="action")
    def after_each(action):
        print(f"Action '{action.name}' status is '{action.status}'")

    @teardown(scope="session")
    def after_all(actions):
        print(f"Executed {len(actions)} action(s)")
    ```

    By default, runs teardowns in `action` scope.

    **Note:** If fixtures are defined in another file, they need to be imported
     in the main actions file to be taken into use
    """
    from robocorp.tasks import teardown as _teardown

    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        return _teardown(*args, **kwargs)

    scope = kwargs.pop("scope", "action")
    if scope == "action":
        scope = "task"

    elif scope == "session":
        pass

    else:
        raise ValueError(f"Unknown scope '{scope}', expected 'action' or 'session'")

    kwargs["scope"] = scope
    return _teardown(*args, **kwargs)
