"""A library for interacting with Control Room work items.

Work items are used for managing data that go through multiple
steps and tasks inside a process. Each step of a process receives
input work items from the previous step, and creates output work items for
the next step.

**Item structure**

A work item's data payload is JSON and allows storing anything that is
serializable. This library by default interacts with payloads that
are a dictionary of key-value pairs, which it treats as individual
variables. These variables can be exposed to the Robot Framework task
to be used directly.

In addition to the data section, a work item can also contain files,
which are stored by default in Robocorp Control Room. Adding and using
files with work items requires no additional setup from the user.

**Loading inputs**

The library automatically loads the first input work item, if the
library input argument ``autoload`` is truthy (default).

After an input has been loaded its payload and files can be accessed
through corresponding keywords, and optionally these values can be modified.

**E-mail triggering**

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
from typing import Callable, Iterator, Optional, Union

from robocorp.tasks import get_current_task, task_cache

from ._context import Context
from ._exceptions import EmptyQueue, to_exception_type
from ._types import ExceptionType, JSONType, State
from ._workitem import Input, Output

__version__ = "0.4.0"
version_info = [int(x) for x in __version__.split(".")]

LOGGER = logging.getLogger(__name__)


@task_cache
def _context():
    ctx = Context()
    yield ctx

    for item in ctx.outputs:
        if not item.saved:
            logging.warning("%s has unsaved changes that will be discarded", item)

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


class Inputs:
    def __iter__(self):
        while True:
            try:
                with self.reserve() as item:
                    yield item
            except EmptyQueue:
                break

    @property
    def current(self) -> Optional[Input]:
        return _context().current_input

    @property
    def released(self) -> list[Input]:
        return [item for item in _context().inputs if item.released]

    def reserve(self) -> Input:
        return _context().reserve_input()


class Outputs:
    def __len__(self):
        return len(_context().outputs)

    def __getitem__(self, key):
        return _context().outputs[key]

    def __iter__(self):
        return iter(_context().outputs)

    def __reversed__(self):
        return reversed(_context().outputs)

    @property
    def last(self) -> Optional[Output]:
        if not _context().outputs:
            return None

        return _context().outputs[-1]

    def create(
        self,
        payload: Optional[JSONType] = None,
        files: Optional[Union[str, list[str]]] = None,
        save: bool = True,
    ) -> Output:
        item = _context().create_output()

        if payload is not None:
            item.payload = payload

        if files is not None:
            for path in files:
                item.add_file(path)

        if save:
            item.save()

        return item


inputs = Inputs()
outputs = Outputs()


__all__ = [
    "State",
    "ExceptionType",
    "Input",
    "Output",
    "inputs",
    "outputs",
]
