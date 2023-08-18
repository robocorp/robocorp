# Modifying inputs

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

