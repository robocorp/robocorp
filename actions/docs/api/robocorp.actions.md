<!-- markdownlint-disable -->

# module `robocorp.actions`

**Source:** [`__init__.py:0`](https://github.com/robocorp/robocorp/tree/master/actions/src/robocorp/actions/__init__.py#L0)

______________________________________________________________________

## function `action`

**Source:** [`__init__.py:25`](https://github.com/robocorp/robocorp/tree/master/actions/src/robocorp/actions/__init__.py#L25)

```python
action(*args, **kwargs)
```

Decorator for actions (entry points) which can be executed by `robocorp.actions`.

i.e.:

If a file such as actions.py has the contents below:

```python
from robocorp.actions import action

@action
def enter_user() -> str:
    ...
```

It'll be executable by robocorp actions as:

python -m robocorp.actions run actions.py -a enter_user

**Args:**

- <b>`func`</b>:  A function which is a action to `robocorp.actions`.
- <b>`is_consequential`</b>:  Whether the action is consequential or not. This will add `x-openai-isConsequential: true` to the action metadata and shown in OpenApi spec.

______________________________________________________________________

## function `setup`

**Source:** [`_fixtures.py:24`](https://github.com/robocorp/robocorp/tree/master/actions/src/robocorp/actions/_fixtures.py#L24)

```python
setup(
    *args,
    **kwargs
) → Union[Callable[[ITask], Any], Callable[[Callable[[ITask], Any]], Callable[[ITask], Any]], Callable[[Callable[[Sequence[ITask]], Any]], Callable[[Sequence[ITask]], Any]]]
```

Run code before any actions start, or before each separate action.

Receives as an argument the action or actions that will be run.

Can be used as a decorator without arguments:

```python
from robocorp.actions import setup

@setup
def my_fixture(action):
    print(f"Before action: {action.name}")
```

Alternatively, can be called with a `scope` argument to decide when the fixture is run:

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

The `setup` fixture also allows running code after the execution, if it `yield`s the execution to the action(s):

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

**Note:** If fixtures are defined in another file, they need to be imported in the main actions file to be taken into use

______________________________________________________________________

## function `teardown`

**Source:** [`_fixtures.py:114`](https://github.com/robocorp/robocorp/tree/master/actions/src/robocorp/actions/_fixtures.py#L114)

```python
teardown(
    *args,
    **kwargs
) → Union[Callable[[ITask], Any], Callable[[Callable[[ITask], Any]], Callable[[ITask], Any]], Callable[[Callable[[Sequence[ITask]], Any]], Callable[[Sequence[ITask]], Any]]]
```

Run code after actions have been run, or after each separate action.

Receives as an argument the action or actions that were executed, which contain (among other things) the resulting status and possible error message.

Can be used as a decorator without arguments:

```python
from robocorp.actions import teardown

@teardown
def my_fixture(action):
    print(f"After action: {action.name})
```

Alternatively, can be called with a `scope` argument to decide when the fixture is run:

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

**Note:** If fixtures are defined in another file, they need to be imported in the main actions file to be taken into use

______________________________________________________________________

## function `session_cache`

**Source:** [`__init__.py:65`](https://github.com/robocorp/robocorp/tree/master/actions/src/robocorp/actions/__init__.py#L65)

```python
session_cache(func)
```

Provides decorator which caches return and clears automatically when all actions have been run.

A decorator which automatically cache the result of the given function and will return it on any new invocation until robocorp-actions finishes running all actions.

The function may be either a generator with a single yield (so, the first yielded value will be returned and when the cache is released the generator will be resumed) or a function returning some value.

**Args:**

- <b>`func`</b>:  wrapped function.

______________________________________________________________________

## function `action_cache`

**Source:** [`__init__.py:86`](https://github.com/robocorp/robocorp/tree/master/actions/src/robocorp/actions/__init__.py#L86)

```python
action_cache(func)
```

Provides decorator which caches return and clears it automatically when the current action has been run.

A decorator which automatically cache the result of the given function and will return it on any new invocation until robocorp-actions finishes running the current action.

The function may be either a generator with a single yield (so, the first yielded value will be returned and when the cache is released the generator will be resumed) or a function returning some value.

**Args:**

- <b>`func`</b>:  wrapped function.

______________________________________________________________________

## function `get_output_dir`

**Source:** [`__init__.py:107`](https://github.com/robocorp/robocorp/tree/master/actions/src/robocorp/actions/__init__.py#L107)

```python
get_output_dir() → Optional[Path]
```

Provide the output directory being used for the run or None if there's no output dir configured.

______________________________________________________________________

## function `get_current_action`

**Source:** [`__init__.py:117`](https://github.com/robocorp/robocorp/tree/master/actions/src/robocorp/actions/__init__.py#L117)

```python
get_current_action() → Optional[ITask]
```

Provides the action which is being currently run or None if not currently running an action.

______________________________________________________________________

## class `ITask`

**Source:** [`_protocols.py:51`](https://github.com/robocorp/robocorp/tree/master/actions/.venv/lib/python3.10/site-packages/robocorp/tasks/_protocols.py#L51)

#### property `failed`

Returns true if the task failed. (in which case usually exc_info is not None).

#### property `input_schema`

#### property `lineno`

#### property `name`

#### property `output_schema`

______________________________________________________________________

### method `run`

**Source:** [`_protocols.py:82`](https://github.com/robocorp/robocorp/tree/master/actions/.venv/lib/python3.10/site-packages/robocorp/tasks/_protocols.py#L82)

```python
run() → Any
```

______________________________________________________________________

## enum `Status`

**Source:** [`_protocols.py:43`](https://github.com/robocorp/robocorp/tree/master/actions/.venv/lib/python3.10/site-packages/robocorp/tasks/_protocols.py#L43)

Task state

### Values

- **NOT_RUN** = NOT_RUN
- **PASS** = PASS
- **FAIL** = FAIL
