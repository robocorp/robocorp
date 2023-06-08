# robocorp-workitems

Work items are used in Robocorp Control Room for managing data that go through
multiple steps and tasks inside a process. Each step of a process receives input
work items from the previous step, and creates output work items for the next
step.

## Installation

The library can be installed from pip:

```bash
pip install robocorp-workitems
```

## Usage

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

## Work item structure

A work item's data payload is JSON and allows storing anything that is JSON
serializable. By default the payload is a mapping of key-value pairs.

In addition to the payload section, a work item can also contain files, which
are stored within Robocorp Control Room. Adding and using files with work items
requires no additional setup from the user.

## Reserving and releasing input items

When an execution in Control Room starts, the first input item is automatically
reserved. This first item is also loaded by the library when the task execution
starts.

After an item has been handled, it should be released as either passed or
failed. There can only be one reserved input item at a time.

Reserving can be done explicitly by calling the reserve method, which also acts
as a context manager:

```python
with workitems.inputs.reserve() as item:
    print("Handling item!")
```

Another option is to loop through all inputs, which implicitly reserves and
releases the corresponding items:

```python
for item in workitems.inputs:
    print("Handling item!")
```

Releasing can also be done explicitly to set specific errors, or to mark items
as done before exiting the block:

```python
for item in workitems.inputs:
    order_id = item.payload["order_id"]

    if not is_valid_id(order_id):
        item.fail(code="INVALID_ID", message=f"Invalid order id: {order_id}")

    ...

    item.done()
```

## Creating outputs

For each input work item, you can create any amount of output work items.
These will be forwarded to the next step of a process, or set as the final
result if there are no further steps.

In most cases, it's enough to create an output item directly using
the `outputs` object:

```python
workitems.outputs.create(
    payload={"key": "value"},
    files=["path/to/file.txt"],
)
```

Internally, Control Room keeps a relationship between the parent and child
work items. The above example always uses the currently reserved item as the
parent, but it's also possible to create an output explicitly from
the input item:

```python
with workitems.inputs.reserve() as input_item:
    input_item.create_output(payload={"key": "value"})
```

In some cases, it's also useful to create an output item and then modify it
before saving:

```python
item = workitems.outputs.create(save=False)

for index, path in enumerate(directory.glob("*.pdf")):
    item.add_file(path, name=f"document-{index}")

item.save()
```

## Email triggering

Since a process can be started in Control Room by sending an email, the payload
and files can contain the email metadata, text, and possible attached files.
This requires the `Parse email` configuration option to be enabled.

The input work item in this library has a helper method `email()`, which can
be used to parse it into a typed container:

```python
item = workitems.inputs.current
email = item.email()

print("Email sent by:", email.from_.address)
print("Email subject:", email.subject)

payload = json.loads(email.text)
print("Received JSON payload:", payload)
```

To learn more about email triggering, see
[the docs page](https://robocorp.com/docs/control-room/attended-or-unattended/email-trigger).

## Local development

### Using the VSCode extension

If you are developing in VSCode with the [Robocorp Code extension](https://robocorp.com/docs/setup/development-environment#visual-studio-code-with-robocorp-extensions),
you can utilize the built in local development features described in the
[Developing with work items locally](https://robocorp.com/docs/development-guide/control-room/work-items#developing-with-work-items-locally)
section of the [Using work items](https://robocorp.com/docs/development-guide/control-room/work-items)
development guide.

This allows you to develop and test your work items before deploying
to Control Room.

### Using a custom editor

It's also possible to develop locally with a custom editor, but it requires
some configuration.

To enable the development mode for the library, you should set the environment
variable `RC_WORKITEM_ADAPTER` with the value `FileAdapter`. This tells the
library to use local files for simulating input and output queues for work
items, in the form of JSON files.

The environment variables `RC_WORKITEM_INPUT_PATH` and `RC_WORKITEM_OUTPUT_PATH`
are also required, and should contain the paths to the input and output JSON
files. The output file will be created by the library, but the input file
should be created manually.

An example of an input file with one work item:

```json
[
    {
        "payload": {
            "variable1": "a-string-value",
            "variable2": ["a", "list", "value"]
        },
        "files": {
            "file1": "path/to/file.ext"
        }
    }
]
```
