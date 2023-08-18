# Flow control with exceptions

Failures for input work items can be set explicitly with the `fail()` method,
which takes in an exception type (e.g. `BUSINESS` or `APPLICATION`), and an
optional custom error code and human-readable message.

However, sometimes complicated business logic needs to fail the entire input
item within a function that does not have direct access to it. For this use-case
the library exposes two exceptions: `BusinessException` and `ApplicationException`.

When the library catches either of these exceptions, it knows to use it to set
the failure state of the work item accordingly.

## Example usage

```python
from robocorp import workitems
from robcorp.tasks import task


@task
def handle_transactions():
    with workitems.inputs.current as item:
        handle_transaction(item.payload)


def handle_transaction(data):
    check_valid_id(data["transactionId"])
    ...


def check_valid_id(value):
    if len(value) < 8:
        raise workitems.BusinessException(
            code="INVALID_ID",
            message="Transaction ID length is too short!",
        )
```

## Error boundaries

Where the exceptions are caught depends on the calling code, as there
are several boundaries where it can happen.

### Task end

The outermost boundary is the task itself. If a library exception is thrown
from within the task and no other code catches it, the values are used to set
the input work item's state before the task fails.

```python
from robocorp import workitems
from robcorp.tasks import task


@task
def task_boundary():
    raise workitems.ApplicationException("Oops, always fails")
```

**Note:** The task itself will always fail when an exception is caught on this level.

### Context manager

A reserved input item can be used as a context manager, which automatically
sets the pass or fail state depending on whether an exception happens before
exiting the block or not.

```python
from robocorp import workitems
from robcorp.tasks import task


@task
def context_boundary():
    # Sets the work item's state as completed after exiting the block
    with workitems.inputs.current:
        pass

    # Sets the work item's state as failed when catching the exception
    with workitems.inputs.reserve():
        raise workitems.ApplicationException("Something went wrong")
        print("This does not run")

    print("This runs")
```

**Note:** When the context manager catches a work item exception, it continues without
failing the entire task.

### Looping inputs

While iterating the input queue automatically reserves and releases items,
it can't catch the exceptions while iterating. If these exceptions are used
in a looping task, they should be combined as follows:

```python
import random
from robocorp import workitems
from robcorp.tasks import task


@task
def loop_boundary():
    # Loops through all work items, even though some of them throw an exception
    for item in workitems.inputs:
        with item:
            if random.choice([True, False]):
                raise workitems.ApplicationException("Random failure")
```
