# robocorp-workitems

Work items are used in Robocorp Control Room for managing data that go through
multiple steps and tasks inside a process. Each step of a process receives input
work items from the previous step, and creates output work items for the next
step.

## Getting started

The library exposes two objects, `inputs` and `outputs`, which are the main way
to interact with work item queues. The former deals with the reading input work
items, and the latter with creating output work items.

A run inside Control Room will always have at least one work item available to
it. The simplest Robot which reads the current work item and creates an output
can be done in the following manner:

```python
from robocorp import workitems
from robocorp.tasks import task

@task
def handle_item():
    item = workitems.inputs.current
    print("Received payload:", item.payload)
    workitems.outputs.create(payload={"key": "value"})
```

Iterating over all available input items in the queue is also easy:

```python
from robocorp import workitems
from robocorp.tasks import task

@task
def handle_all_items():
    for item in workitems.inputs:
        print("Received payload:", item.payload)
        workitems.outputs.create(payload={"key": "value"})
```

### Work item structure

A work item's data payload is JSON and allows storing anything that is JSON
serializable. By default the payload is a mapping of key-value pairs.

In addition to the payload section, a work item can also contain files, which
are stored within Robocorp Control Room. Adding and using files with work items
requires no additional setup from the user.

## Guides

- [Reserving and releasing input items](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/00-reserving-inputs.md)
- [Creating outputs](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/01-creating-outputs.md)
- [Local development](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/02-local-development.md)
- [Email triggering](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/03-email-triggering.md)
- [Collecting all inputs](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/04-collecting-inputs.md)
- [Flow control with exceptions](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/05-input-exceptions.md)
- [Modifying inputs](https://github.com/robocorp/robocorp/blob/master/workitems/docs/guides/06-modifying-inputs.md)

Further user guides and tutorials can be found in [Robocorp Docs](https://robocorp.com/docs).

## API Reference

Information on specific functions or classes: [robocorp.workitems](https://github.com/robocorp/robocorp/blob/master/workitems/docs/api/robocorp.workitems.md)

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/workitems/docs/CHANGELOG.md).
