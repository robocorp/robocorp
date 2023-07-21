# robocorp-workitems

Work items are used in Robocorp Control Room for managing data that go through
multiple steps and tasks inside a process. Each step of a process receives input
work items from the previous step, and creates output work items for the next
step.

## Getting started

The library exposes two objects, `inputs` and `outputs`, which are the main way
to interact with work item queues. The former deals with the reading input work
items, and the latter with creating output work items.

Iterating over inputs and creating outputs is easy:

```python
from robocorp import workitems

def read_inputs_and_create_outputs():
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

- [Reserving and releasing input items](./guides/reserving-inputs.md)
- [Creating outputs](./guides/creating-outputs.md)
- [Email triggering](./guides/email-triggering.md)
- [Local development](./guides/local-development.md)

Further user guides and tutorials can be found in [Robocorp Docs](https://robocorp.com/docs).

## API Reference

Information on specific functions or classes: [robocorp.workitems](./api/robocorp.workitems.md)

## Changelog

A list of releases and corresponding changes can be found in the [changelog](./CHANGELOG.md).
