"""A library for interacting with Control Room work items.

Work items are used for managing data that go through multiple
steps and tasks inside a process. Each step of a process receives
input work items from the previous step, and creates output work items for
the next step.

**Installation**

The library can be installed from pip::

    pip install robocorp-workitems

**Usage**

The library exposes two instances, `inputs` and `outputs`, which are the
main way to interact with work items. The former deals with the queue of
input work items, and the latter with creating output work items.

Iterating over inputs and creating inputs is easy::

    from robocorp import workitems

    def read_inputs_and_create_outputs():
        for item in workitems.inputs:
            print("Received payload:", item.payload)
            workitems.outputs.create(payload={"key": "value"})

**Work item structure**

A work item's data payload is JSON and allows storing anything that is JSON
serializable. By default the payload is a mapping of key-value pairs.

In addition to the payload section, a work item can also contain files,
which are stored within Robocorp Control Room. Adding and using
files with work items requires no additional setup from the user.

**Reserving and releasing input items**

When an execution in Control Room starts, the first input item is automatically
reserved. This first item is also loaded by the library when the task execution
starts.

After the item has been handled, it should be released as either passed or failed.
There can only be one reserved input item at a time.

Reserving can be done by either explicitly calling the reserve method,
which also acts as a context manager::

    with workitems.inputs.reserve() as item:
        print("Handling item!")

Another option is to loop through all inputs, which implicitly reserves and releases
the corresponding items::

    for item in workitems.inputs:
        print("Handling item!")

Releasing can also be done explicitly, to set specific errors, or to mark items
as done

**Email triggering**

Since a process can be started in Control Room by sending an e-mail, a body
in Text/JSON/YAML/HTML format can be sent as well and this gets attached to the
input work item with the ``rawEmail`` payload variable. This library automatically
parses the content of it and saves into ``parsedEmail`` the dictionary
transformation of the original e-mail.

If "Parse email" Control Room configuration option is enabled (recommended), then
your e-mail is automatically parsed in the work item under the ``email`` payload
variable, which is a dictionary containing a ``body`` holding the final parsed form
of the interpreted e-mail body. The payload variable ``parsedEmail`` is still
available for backwards compatibility reasons and holds the very same body inside
the ``parsedEmail[Body]``.

E-mail attachments will be added into the work item as files. Read more on:
https://robocorp.com/docs/control-room/attended-or-unattended/email-trigger

Example:

After starting the process by sending an e-mail with a body like:

.. code-block:: json

    {
        "message": "Hello world!"
    }

The robot can use the parsed e-mail body's dictionary:

.. code-block:: robotframework

    *** Tasks ***
    Using Prased Emails
        ${mail} =    Get Work Item Variable    email
        Set Work Item Variables    &{mail}[body]
        ${message} =     Get Work Item Variable     message
        Log    ${message}    # will print "Hello world!"

The behaviour can be disabled by loading the library with
``auto_parse_email=${None}`` or altered by providing to it a dictionary with one
"key: value" where the key is usually "email.text" (deprecated "rawEmail", the
variable set by Control Room, which acts as source for the parsed (deprecated raw)
e-mail data) and the value can be "email.body" (deprecated "parsedEmail", where the
parsed e-mail data gets stored into), value which can be customized and retrieved
with ``Get Work Item Variable``.

**Creating outputs**

It's possible to create multiple new work items as an output from a
task. With the keyword ``Create Output Work Item`` a new empty item
is created as a child for the currently loaded input.

All created output items are sent into the input queue of the next
step in the process.

**Active work item**

Keywords that read or write from a work item always operate on the currently
active work item. Usually that is the input item that has been automatically
loaded when the execution started, but the currently active item is changed
whenever the keywords ``Create Output Work Item`` or ``Get Input Work Item``
are called. It's also possible to change the active item manually with the
keyword ``Set current work item``.

**Saving changes**

While a work item is loaded automatically when a suite starts, changes are
not automatically reflected back to the source. The work item will be modified
locally and then saved when the keyword ``Save Work Item`` is called.
This also applies to created output work items.

It is recommended to defer saves until all changes have been made to prevent
leaving work items in a half-modified state in case of failures.

**Local Development**

While Control Room is the default implementation, it can also be replaced
with a custom adapter. The selection is based on either the ``default_adapter``
argument for the library, or the ``RPA_WORKITEMS_ADAPTER`` environment
variable. The library has a built-in alternative adapter called FileAdapter for
storing work items to disk.

The FileAdapter uses a local JSON file for input work items.
It's a list of work items, each of which has a data payload and files.

An example of a local file with one work item:

.. code-block:: json

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

Output work items (if any) are saved to an adjacent file
with the same name, but with the extension ``.output.json``. You can specify
through the "RPA_OUTPUT_WORKITEM_PATH" env var a different path and name for this
file.

**Simulating the Cloud with Robocorp Code VSCode Extension**

If you are developing in VSCode with the `Robocorp Code extension`_, you can
utilize the built in local development features described in the
`Developing with work items locally`_ section of the
`Using work items`_ development guide.

.. _Robocorp Code extension: https://robocorp.com/docs/setup/development-environment#visual-studio-code-with-robocorp-extensions
.. _Developing with work items locally: https://robocorp.com/docs/development-guide/control-room/work-items#developing-with-work-items-locally
.. _Using work items: https://robocorp.com/docs/development-guide/control-room/work-items
"""  # noqa: E501
import logging
from typing import Callable, Optional, Union, cast

from robocorp.tasks import get_current_task, task_cache

from ._context import Context
from ._exceptions import (
    ApplicationException,
    BusinessException,
    EmptyQueue,
    to_exception_type,
)
from ._types import ExceptionType, JSONType, State
from ._workitem import Input, Output

__version__ = "0.4.0"
version_info = [int(x) for x in __version__.split(".")]

LOGGER = logging.getLogger(__name__)


@task_cache
def __ctx():
    """Create a shared context for the task execution.

    Automatically loads the first input item, as one is always automatically
    reserved from the queue by Control Room.

    After the task finishes, logs a warning if any output work items are
    unsaved, and releases the current input if the task failed with an
    exception.
    """
    ctx = Context()
    ctx.reserve_input()

    yield ctx

    for item in ctx.outputs:
        if not item.saved:
            LOGGER.warning("%s has unsaved changes that will be discarded", item)

    current = ctx.current_input
    if current is None or current.released:
        return

    task = get_current_task()
    if not task:
        return

    if task.exc_info is not None:
        exc_type, exc_value, _ = task.exc_info
        exception_type = to_exception_type(exc_type)
        current.fail(exception_type, message=str(exc_value))


# Workaround for @task_cache handling the generator
_ctx = cast(Callable[[], Context], __ctx)


class Inputs:
    """Inputs represents the input queue of work items.

    It can be used to reserve and release items from the queue,
    and iterate over them.

    Example:
        Multiple items can behandled by iterating over this class::

            for item in inputs:
                handle_item(item.payload)
    """

    def __iter__(self):
        if self.current and not self.current.released:
            with self.current as item:
                yield item

        while True:
            try:
                with self.reserve() as item:
                    yield item
            except EmptyQueue:
                break

    @property
    def current(self) -> Optional[Input]:
        """The current reserved input item."""
        return _ctx().current_input

    @property
    def released(self) -> list[Input]:
        """A list of inputs reserved and released during the lifetime
        of the library.
        """
        return [item for item in _ctx().inputs if item.released]

    def reserve(self) -> Input:
        """Reserve a new input work item.

        There can only be one item reserved at a time.

        Returns:
            Input work item

        Raises:
            RuntimeError: An input work item is already reserved
            workitems.EmptyQueue: There are no further items in the queue
        """
        return _ctx().reserve_input()


class Outputs:
    """Outputs represents the output queue of work items.

    It can be used to create outputs and inspect the items created during the execution.

    Example:
        The class can be used to create outputs::

            outputs.create({"key": "value"})
    """

    def __len__(self):
        return len(_ctx().outputs)

    def __getitem__(self, key):
        return _ctx().outputs[key]

    def __iter__(self):
        return iter(_ctx().outputs)

    def __reversed__(self):
        return reversed(_ctx().outputs)

    @property
    def last(self) -> Optional[Output]:
        """The most recently created output work item, or `None`."""
        if not _ctx().outputs:
            return None

        return _ctx().outputs[-1]

    def create(
        self,
        payload: Optional[JSONType] = None,
        files: Optional[Union[str, list[str]]] = None,
        save: bool = True,
    ) -> Output:
        """Create a new output work item, which can have both a JSON
        payload and attached files.

        Creating an output item requires an input to be currently reserved.

        Args:
            payload: JSON serializable data (dict, list, scalar, etc.)
            files: List of paths to files or glob pattern
            save: Immediately save item after creation

        Raises:
            RuntimeError: No input work item reserved
        """
        item = _ctx().create_output()

        if payload is not None:
            item.payload = payload

        if files is not None:
            if isinstance(files, str):
                item.add_files(pattern=files)
            else:
                for path in files:
                    item.add_file(path=path)

        if save:
            item.save()

        return item


inputs = Inputs()
outputs = Outputs()

__all__ = [
    "EmptyQueue",
    "BusinessException",
    "ApplicationException",
    "State",
    "ExceptionType",
    "Input",
    "Output",
    "inputs",
    "outputs",
]
