# Advanced patterns

## Modifying inputs

Although not recommended, it's possible to modify input work items.
As an example, a process might need to store additional metadata for failed items.

This is potentially dangerous, as it will reduce traceability of the process
and maybe even make it behave in unexpected ways. If a modified item is retried,
it could result in something that was not intended.

With these caveats, modifying an input item is relatively easy:

```python
from robocorp import workitems
from robocorp.tasks import task


@task
def clear_payload():
    # NOTE: This is not recommended
    item = workitems.inputs.current
    item.payload = None
    item.save()
```

This example would clear all payloads from input work items.

## Reducing inputs

Sometimes it's necessary to reduce multiple input work items into one
output work item, e.g. for reporting purposes. The tricky part is that
there needs to be a reserved input work item to create an output, and there
is an unknown amount of input work items. This means that it's not possible
to first loop all inputs and then create the output.

One way to solve this is to create an output from the first item, and
then modify it later:

```python
from robocorp import workitems
from robocorp.tasks import task


@task
def summarize():
    output = workitems.outputs.create()

    errors = []
    for item in workitems.inputs:
        if error := item.payload.get("error"):
            errors.append(error)

    output.payload = {"errors": errors}
    output.save()
```
