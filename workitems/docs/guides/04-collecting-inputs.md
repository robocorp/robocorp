# Collecting all inputs

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
