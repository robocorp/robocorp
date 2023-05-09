import email
import fnmatch
import json
import logging
import os
from glob import glob
from pathlib import Path
from threading import Event
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple, Type, Union

import yaml

from robocorp.workitems._workitems._adapter import (
    UNDEFINED,
    BaseAdapter,
    EmptyQueue,
    RobocorpAdapter,
)
from robocorp.workitems._workitems._utils import (
    deprecation,
    get_decoded_email_body,
    get_dot_value,
    import_by_name,
    required_env,
    set_dot_value,
)
from robocorp.workitems.workitem import Error, State, WorkItem

ENCODING = "utf-8"

_STRINGS_TYPE = Union[str, Tuple[str, ...]]
AUTO_PARSE_EMAIL_TYPE = Optional[Dict[_STRINGS_TYPE, _STRINGS_TYPE]]
AUTO_PARSE_EMAIL_DEFAULT = {
    # Source payload keys or file names -> destination payload keys with the parsed
    # e-mail content.
    ("email.text", "__mail.html"): ("email.body", "parsedEmail.Body"),
    "rawEmail": "parsedEmail",
}


class _WorkItemsLibrary:
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

    **Examples**

    **Robot Framework**

    In the following example a task creates an output work item,
    and attaches some variables to it.

    .. code-block:: robotframework

        *** Settings ***
        Library    RPA.Robocorp.WorkItems

        *** Tasks ***
        Save variables to Control Room
            Create Output Work Item
            Set work item variables    user=Dude    mail=address@company.com
            Save Work Item

    In the next step of the process inside a different robot, we can use
    previously saved work item variables. Also note how the input work item is
    loaded implicitly when the suite starts.

    .. code-block:: robotframework

        *** Settings ***
        Library    RPA.Robocorp.WorkItems

        *** Tasks ***
        Use variables from Control Room
            Set task variables from work item
            Log    Variables are now available: s${user}, ${mail}

    **Python**

    The library can also be used through Python, but it does not implicitly
    load the first work item.

    .. code-block:: python

        import logging
        from RPA.Robocorp.WorkItems import WorkItems

        def list_variables(item_id):
            library = WorkItems()
            library.get_input_work_item()

            variables = library.get_work_item_variables()
            for variable, value in variables.items():
                logging.info("%s = %s", variable, value)
    """  # noqa: E501

    EMAIL_BODY_LOADERS = [
        ("JSON", json.loads),
        ("YAML", yaml.full_load),
    ]

    def __init__(
        self,
        autoload: bool = True,
        root: Optional[str] = None,
        default_adapter: Union[Type[BaseAdapter], str] = RobocorpAdapter,
        # pylint: disable=dangerous-default-value
        auto_parse_email: AUTO_PARSE_EMAIL_TYPE = AUTO_PARSE_EMAIL_DEFAULT,
    ):
        #: Current selected work item
        self._current: Optional[WorkItem] = None
        #: Input work items
        self.inputs: List[WorkItem] = []
        #: Output work items
        self.outputs: List[WorkItem] = []
        #: Variables root object in payload
        self.root = root
        #: Auto-load first input item and automatically parse e-mail content if
        # present.
        self.autoload: bool = autoload
        self._auto_parse_email = auto_parse_email
        #: Adapter for reading/writing items
        self._adapter_class = self._load_adapter(default_adapter)
        self._adapter: Optional[BaseAdapter] = None

        # Know when we're iterating (and consuming) all the work items in the queue.
        self._under_iteration = Event()

    @property
    def adapter(self):
        if self._adapter is None:
            self._adapter = self._adapter_class()
        return self._adapter

    @property
    def current(self) -> WorkItem:
        if self._current is None:
            raise RuntimeError("No active work item")

        return self._current

    @current.setter
    def current(self, value):
        if not isinstance(value, WorkItem):
            raise ValueError(f"Not a work item: {value}")

        self._current = value

    def _load_adapter(self, default) -> Type[BaseAdapter]:
        """Load adapter by name, using env or given default."""
        adapter = required_env("RPA_WORKITEMS_ADAPTER", default)

        if isinstance(adapter, str):
            adapter = import_by_name(adapter, __name__)

        assert issubclass(
            adapter, BaseAdapter
        ), "Adapter does not inherit from BaseAdapter"

        return adapter

    @classmethod
    def _interpret_content(cls, body: str) -> Union[dict, str]:
        for name, loader in cls.EMAIL_BODY_LOADERS:
            try:
                body = loader(body)
            except Exception as exc:  # pylint: disable=broad-except
                logging.debug(
                    "Failed deserializing input e-mail body content with loader %r "
                    "due to: %s",
                    name,
                    exc,
                )
            else:
                break

        return body

    def _get_email_content(
        self, variables: Dict
    ) -> Optional[Tuple[str, bool, Tuple[str]]]:
        # Returns the extracted e-mail [parsed] content and its payload destination.
        to_tuple = (
            lambda keys: keys if isinstance(keys, tuple) else (keys,)
        )  # noqa: E731
        file_list = self.list_work_item_files()
        for input_keys, output_keys in self._auto_parse_email.items():
            input_keys = to_tuple(input_keys)
            for input_key in input_keys:
                try:
                    content = get_dot_value(variables, input_key)
                except AttributeError:
                    content = None  # couldn't reach final destination
                if not content and input_key in file_list:
                    path = Path(self.get_work_item_file(input_key))
                    content = path.read_text(encoding=ENCODING)
                    path.unlink()
                if content:
                    parsed = not input_key == "rawEmail"
                    if not parsed:
                        deprecation(
                            "Legacy non-parsed e-mail trigger detected! Please enable "
                            '"Parse email" configuration option in Control Room. (more'
                            " details: https://robocorp.com/docs/control-room/attended"
                            "-or-unattended/email-trigger#parse-email)"
                        )
                    output_keys = to_tuple(output_keys)
                    return content, parsed, output_keys
        return None

    def _parse_work_item_from_email(self):
        # Parse and return a dictionary from the input work item of a process started
        #  by e-mail trigger.
        if not self._auto_parse_email:
            return  # auto e-mail parsing disabled

        try:
            variables = self.get_work_item_variables()
        except ValueError:
            return  # payload not a dictionary

        content_details = self._get_email_content(variables)
        if not content_details:
            return  # no e-mail content found in the work item

        content, parsed, output_keys = content_details
        if parsed:  # With "Parse email" Control Room configuration option enabled.
            email_data = self._interpret_content(content)
        else:  # With "Parse email" Control Room configuration option disabled.
            # pylint: disable=no-member
            message = email.message_from_string(content)
            message_dict = dict(message.items())
            body, has_attachments = get_decoded_email_body(message)
            message_dict["Body"] = self._interpret_content(body)
            message_dict["Has-Attachments"] = has_attachments
            email_data = message_dict

        for output_key in output_keys:
            keys = output_key.split(".", 1)
            parsed_email = self.get_work_item_variable(keys[0], default={})
            if len(keys) == 2:
                set_dot_value(parsed_email, keys[1], value=email_data)
            else:
                parsed_email = email_data
            # pylint: disable=undefined-loop-variable
            self.set_work_item_variable(keys[0], parsed_email)

    # TODO: Add to init
    def _start_suite(self, *_):
        """Robot Framework listener method, called when suite starts."""
        if not self.autoload:
            return

        try:
            self.get_input_work_item()
        # pylint: disable=broad-except
        except Exception as exc:
            logging.warning("Failed to load input work item: %s", exc)
        finally:
            self.autoload = False

    # TODO: Proper handling in case of failure
    def _release_on_failure(self, attributes):
        """Automatically releases current input Work Item when encountering failures
        with tasks and/or suites.
        """
        if attributes["status"] != "FAIL":
            return

        message = attributes["message"]
        logging.info("Releasing FAILED input item with APPLICATION error: %s", message)
        self.release_input_work_item(
            state=State.FAILED,
            exception_type=Error.APPLICATION,
            message=message,
            _auto_release=True,
        )

    # TODO: Add atexit handler?
    def _end_suite(self, _, attributes):
        """Robot Framework listener method, called when the suite ends."""
        # pylint: disable=unused-argument
        for item in self.inputs + self.outputs:
            if item.is_dirty:
                logging.warning(
                    "%s has unsaved changes that will be discarded", self.current
                )

        self._release_on_failure(attributes)

    def _end_test(self, _, attributes):
        """Robot Framework listener method, called when each task ends."""
        self._release_on_failure(attributes)

    def set_current_work_item(self, item: WorkItem):
        # pylint: disable=anomalous-backslash-in-string
        """Set the currently active work item.

        The current work item is used as the target by other keywords
        in this library.

        Keywords \`Get Input Work Item\` and \`Create Output Work Item\`
        set the active work item automatically, and return the created
        instance.

        With this keyword the active work item can be set manually.

        Robot Framework Example:

        .. code-block:: robotframework

            *** Tasks ***
            Creating outputs
                ${input}=    Get Input Work Item
                ${output}=   Create Output Work Item
                Set current work item    ${input}

        Python Example:

        .. code-block:: python

            from RPA.Robocorp.WorkItems import WorkItems

            wi = WorkItems()
            parent_wi = wi.get_input_work_item()
            child_wi = wi.create_output_work_item()
            wi.set_current_work_item(parent_wi)
        """  # noqa: W605
        self.current = item

    def get_input_work_item(self, _internal_call: bool = False):
        """Load the next work item from the input queue, and set it as the active work
        item.

        Each time this is called, the previous input work item is released (as DONE)
        prior to reserving the next one.
        If the library import argument ``autoload`` is truthy (default),
        this is called automatically when the Robot Framework suite
        starts.
        """
        if not _internal_call:
            self._raise_under_iteration("Get Input Work Item")

        # Automatically release (with success) the lastly retrieved input work item
        # when asking for the next one.
        self.release_input_work_item(State.DONE, _auto_release=True)

        item_id = self.adapter.reserve_input()
        item = WorkItem(item_id=item_id, parent_id=None, adapter=self.adapter)
        item.load()
        self.inputs.append(item)
        self.current = item

        # Checks for raw/parsed e-mail content and parses it if present. This happens
        # with Processes triggered by e-mail.
        self._parse_work_item_from_email()

        return self.current

    def create_output_work_item(
        self,
        variables: Optional[dict] = None,
        files: Optional[Union[str, List[str]]] = None,
        save: bool = False,
        parent: Optional[WorkItem] = None,
    ) -> WorkItem:
        """Create a new output work item with optional variables and files.

        An output work item is always created as a child for an input item, therefore
        a non-released input is required to be loaded first.
        All changes to the work item are done locally and are sent to the output queue
        after the keyword ``Save Work Item`` is called only, except when `save` is
        `True`.

        Args:
            variables: Optional dictionary with variables to be set into the new output work item.
            files: Optional list or comma separated paths to files to be included into the new output work item.
            save: Automatically call ``Save Work Item`` over the newly created output work item.
            parent: WorkItem to set as a parent of the created item, if given. Otherwise, use current input.

        Returns:
            (WorkItem): The newly created output work item object.

        **Examples**

        **Robot Framework**

        .. code-block:: robotframework

            *** Tasks ***
            Create output items with variables then save
                ${customers} =  Load customer data
                FOR     ${customer}    IN    @{customers}
                    Create Output Work Item
                    Set Work Item Variables    id=${customer.id}
                    ...     name=${customer.name}
                    Save Work Item
                END

            Create and save output items with variables and files in one go
                ${customers} =  Load customer data
                FOR     ${customer}    IN    @{customers}
                    &{customer_vars} =    Create Dictionary    id=${customer.id}
                    ...     name=${customer.name}
                    Create Output Work Item     variables=${customer_vars}
                    ...     files=devdata${/}report.csv   save=${True}
                END

        **Python**

        .. code-block:: python

            from RPA.Robocorp.WorkItems import WorkItems

            wi = WorkItems()
            wi.get_input_work_item()
            customers = wi.get_work_item_variable("customers")
            for customer in customers:
                wi.create_output_work_item(customer, save=True)

        """
        if not self.inputs:
            raise RuntimeError(
                "Unable to create output work item without an input, "
                "call `Get Input Work Item` first"
            )

        parent = parent or self.inputs[-1]
        if parent.state is not None:
            raise RuntimeError(
                "Can't create any more output work items since the last input was "
                "released, get a new input work item first"
            )

        item = WorkItem(item_id=None, parent_id=parent.id, adapter=self.adapter)
        self.outputs.append(item)
        if variables:
            self.set_work_item_variables(item=item, **variables)
        if files:
            if isinstance(files, str):
                files = [path.strip() for path in files.split(",")]
            for path in files:
                # Assumes the name would be the same as the file name itself.
                self.add_work_item_file(path, item=item)
        if save:
            logging.debug("Auto-saving the just created output work item.")
            self.save_work_item(item)

        return item

    def save_work_item(self, item: WorkItem = None):
        """Save the current data and files in the work item. If not saved,
        all changes are discarded when the library goes out of scope.
        """
        item = item or self.current
        item.save()

    def clear_work_item(self):
        """Remove all data and files in the current work item.

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Clearing a work item
                Clear work item
                Save work item

        .. code-block:: python

            from RPA.Robocorp.WorkItems import WorkItems

            wi = WorkItems()
            wi.get_input_work_item()
            wi.clear_work_item()
            wi.save_work_item()
        """
        self.current.payload = {}
        self.remove_work_item_files("*")

    def get_work_item_payload(self):
        """Get the full JSON payload for a work item.

        **NOTE**: Most use cases should prefer higher-level keywords.

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                ${payload}=    Get work item payload
                Log    Entire payload as dictionary: ${payload}
        """
        return self.current.payload

    def set_work_item_payload(self, payload):
        # pylint: disable=anomalous-backslash-in-string
        """Set the full JSON payload for a work item.

        :param payload: Content of payload, must be JSON-serializable

        **NOTE**: Most use cases should prefer higher-level keywords.
        Using this keyword may cause errors when getting the payload via
        the normal \`Get work item variable\` and
        \`Get work item variables\` keywords if you do not set the payload
        to a ``dict``.

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                ${output}=    Create dictionary    url=example.com    username=Mark
                Set work item payload    ${output}

        """  # noqa: W605
        self.current.payload = payload

    def list_work_item_variables(self):
        """List the variable names for the current work item.

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                ${variables}=    List work item variables
                Log    Available variables in work item: ${variables}

        """
        return list(self.get_work_item_variables().keys())

    def get_work_item_variable(self, name, default=UNDEFINED):
        """Return a single variable value from the work item,
        or default value if defined and key does not exist.

        If key does not exist and default is not defined, raises `KeyError`.

        :param name: Name of variable
        :param default: Default value if key does not exist

        Robot Framework Example:

        .. code-block:: robotframework

            *** Tasks ***
            Using a work item
                ${username}=    Get work item variable    username    default=guest

        Python Example:

        .. code-block:: python

            from RPA.Robocorp.WorkItems import WorkItems

            wi = WorkItems()
            wi.get_input_work_item()
            customers = wi.get_work_item_variable("customers")
            print(customers)
        """
        variables = self.get_work_item_variables()
        value = variables.get(name, default)

        if value is UNDEFINED:
            raise KeyError(f"Undefined variable: {name}")

        return value

    def get_work_item_variables(self, item: WorkItem = None):
        """Read all variables from the current work item and
        return their names and values as a dictionary.

        Robot Framework Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                ${variables}=    Get work item variables
                Log    Username: ${variables}[username], Email: ${variables}[email]

        Python Example:

            from RPA.Robocorp.WorkItems import WorkItems
            wi = WorkItems()
            wi.get_input_work_item()
            input_wi = wi.get_work_item_variables()
            print(input_wi["username"])
            print(input_wi["email"])
        """
        item = item or self.current
        payload = item.payload
        if not isinstance(payload, dict):
            raise ValueError(
                f"Expected work item payload to be `dict`, was `{type(payload)}`"
            )

        if self.root is not None:
            return payload.setdefault(self.root, {})

        return payload

    def set_work_item_variable(self, name, value):
        """Set a single variable value in the current work item.

        :param name: Name of variable
        :param value: Value of variable

        Robot Framework Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                Set work item variable    username    MarkyMark
                Save Work Item

        Python Example:

        .. code-block:: python

            from RPA.Robocorp.WorkItems import WorkItems

            customers = [{"id": 1, "name": "Apple"}, {"id": 2, "name": "Microsoft"}]
            wi = WorkItems()
            wi.get_input_work_item()
            wi.set_work_item_variable("customers", customers)
        """
        variables = self.get_work_item_variables()
        logging.info("%s = %s", name, value)
        variables[name] = value

    def set_work_item_variables(self, item: WorkItem = None, **kwargs):
        """Set multiple variables in the current work item.

        :param kwargs: Pairs of variable names and values

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                Set work item variables    username=MarkyMark    email=mark@example.com
                Save Work Item
        """
        variables = self.get_work_item_variables(item)
        for name, value in kwargs.items():
            logging.info("%s = %s", name, value)
            variables[name] = value

    def delete_work_item_variables(self, *names, force=True):
        """Delete variable(s) from the current work item.

        :param names: Names of variables to remove
        :param force: Ignore variables that don't exist in work item

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                Delete work item variables    username    email
                Save Work Item
        """
        variables = self.get_work_item_variables()
        for name in names:
            if name in variables:
                del variables[name]
                logging.info("Deleted variable: %s", name)
            elif not force:
                raise KeyError(f"No such variable: {name}")

    def list_work_item_files(self):
        """List the names of files attached to the current work item.

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                ${names}=    List work item files
                Log    Work item has files with names: ${names}
        """
        return self.current.files

    def get_work_item_file(self, name, path=None) -> str:
        """Get attached file from work item to disk.
        Returns the absolute path to the created file.

        :param name: Name of attached file
        :param path: Destination path of file. If not given, current
                     working directory is used.

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                ${path}=    Get work item file    input.xls
                Open workbook    ${path}
        """
        path = self.current.get_file(name, path)
        logging.info("Downloaded file to: %s", path)
        return path

    def add_work_item_file(
        self,
        path,
        name=None,
        item: WorkItem = None,
    ):
        """Add given file to work item.

        :param path: Path to file on disk
        :param name: Destination name for file. If not given, current name
                     of local file is used.

        **NOTE**: Files are not uploaded before work item is saved

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                Add work item file    output.xls
                Save Work Item
        """
        logging.info("Adding file: %s", path)
        item = item or self.current
        return item.add_file(path, name=name)

    def remove_work_item_file(self, name, missing_ok=True):
        """Remove attached file from work item.

        :param name: Name of attached file
        :param missing_ok: Do not raise exception if file doesn't exist

        **NOTE**: Files are not deleted before work item is saved

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                Remove work item file    input.xls
                Save Work Item
        """
        logging.info("Removing file: %s", name)
        return self.current.remove_file(name, missing_ok)

    def get_work_item_files(self, pattern, dirname=None) -> List[str]:
        """Get files attached to work item that match given pattern.
        Returns a list of absolute paths to the downloaded files.

        :param pattern: Filename wildcard pattern
        :param dirname: Destination directory, if not given robot root is used

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                ${paths}=    Get work item files    customer_*.xlsx
                FOR  ${path}  IN  @{paths}
                    Handle customer file    ${path}
                END
        """
        paths = []
        for name in self.list_work_item_files():
            if fnmatch.fnmatch(name, pattern):
                if dirname:
                    path = self.get_work_item_file(name, os.path.join(dirname, name))
                else:
                    path = self.get_work_item_file(name)
                paths.append(path)

        logging.info("Downloaded %d file(s)", len(paths))
        return paths

    def add_work_item_files(self, pattern):
        """Add all files that match given pattern to work item.

        :param pattern: Path wildcard pattern

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                Add work item files    %{ROBOT_ROOT}/generated/*.csv
                Save Work Item
        """
        matches = glob(pattern, recursive=False)

        paths = []
        for match in matches:
            path = self.add_work_item_file(match)
            paths.append(path)

        logging.info("Added %d file(s)", len(paths))
        return paths

    def remove_work_item_files(self, pattern, missing_ok=True):
        """Removes files attached to work item that match the given pattern.

        :param pattern: Filename wildcard pattern
        :param missing_ok: Do not raise exception if file doesn't exist

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                Remove work item files    *.xlsx
                Save Work Item
        """
        names = []

        for name in self.list_work_item_files():
            if fnmatch.fnmatch(name, pattern):
                name = self.remove_work_item_file(name, missing_ok)
                names.append(name)

        logging.info("Removed %d file(s)", len(names))
        return names

    def _raise_under_iteration(self, action: str) -> None:
        if self._under_iteration.is_set():
            raise RuntimeError(f"Can't {action} while iterating input work items")

    def _ensure_input_for_iteration(self) -> bool:
        last_input = self.inputs[-1] if self.inputs else None
        last_state = last_input.state if last_input else None
        if not last_input or last_state:
            # There are no inputs loaded yet or the last retrieved input work
            # item is already processed. Time for trying to load a new one.
            try:
                self.get_input_work_item(_internal_call=True)
            except EmptyQueue:
                return False

        return True

    def for_each_input_work_item(
        self,
        func: Union[str, Callable],
        *args,
        items_limit: int = 0,
        return_results: bool = True,
        **kwargs,
    ) -> List[Any]:
        """Run a keyword or function for each work item in the input queue.

        Automatically collects and returns a list of results, switch
        ``return_results`` to ``False`` for avoiding this.

        :param func: The RF keyword or Py function you want to map through
            all the work items
        :param args: Variable list of arguments that go into the called keyword/function
        :param kwargs: Variable list of keyword arguments that go into the called
            keyword/function
        :param items_limit: Limit the queue item retrieval to a certain amount,
            otherwise all the items are retrieved from the queue until depletion
        :param return_results: Collect and return a list of results given each
            keyword/function call if truthy

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Log Payloads
                @{lengths} =     For Each Input Work Item    Log Payload
                Log   Payload lengths: @{lengths}

            *** Keywords ***
            Log Payload
                ${payload} =     Get Work Item Payload
                Log To Console    ${payload}
                ${len} =     Get Length    ${payload}
                [Return]    ${len}

        OR

        .. code-block:: python

            import logging
            from RPA.Robocorp.WorkItems import WorkItems

            library = WorkItems()

            def log_payload():
                payload = library.get_work_item_payload()
                print(payload)
                return len(payload)

            def log_payloads():
                library.get_input_work_item()
                lengths = library.for_each_input_work_item(log_payload)
                logging.info("Payload lengths: %s", lengths)

            log_payloads()
        """

        self._raise_under_iteration("iterate input work items")

        to_call = lambda: func(*args, **kwargs)  # noqa: E731
        results = []

        for _ in self.iter_input_work_item(items_limit):
            result = to_call()
            if return_results:
                results.append(result)

        return results if return_results else None

    def iter_input_work_item(
        self,
        items_limit: int = 0,
    ) -> Generator[WorkItem, None, None]:
        self._raise_under_iteration("iterate input work items")

        try:
            self._under_iteration.set()
            count = 0
            while True:
                input_ensured = self._ensure_input_for_iteration()
                if not input_ensured:
                    break

                yield self.current

                self.release_input_work_item(State.DONE, _auto_release=True)

                count += 1
                if items_limit and count >= items_limit:
                    break
        finally:
            self._under_iteration.clear()

    def release_input_work_item(
        self,
        state: Union[State, str],
        exception_type: Optional[Union[Error, str]] = None,
        code: Optional[str] = None,
        message: Optional[str] = None,
        _auto_release: bool = False,
    ):
        """Release the lastly retrieved input work item and set its state.

        This can be released with DONE or FAILED states. With the FAILED state, an
        additional exception can be sent to Control Room describing the problem that
        you encountered by specifying a type and optionally a code and/or message.
        After this has been called, no more output work items can be created
        unless a new input work item has been loaded again.

        :param state: The status on the last processed input work item
        :param exception_type: Error type (BUSINESS, APPLICATION). If this is not
            specified, then the cloud will assume UNSPECIFIED
        :param code: Optional error code identifying the exception for future
            filtering, grouping and custom retrying behaviour in the cloud
        :param message: Optional human-friendly error message supplying additional
            details regarding the sent exception

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                Login into portal
                    ${user} =     Get Work Item Variable    user
                    ${doc} =    Get Work Item Variable    doc
                    TRY
                        Login Keyword    ${user}
                        Upload Doc Keyword    ${doc}

                    EXCEPT    Login Failed
                        Release Input Work Item     FAILED
                        ...    exception_type=APPLICATION
                        ...    code=LOGIN_PORTAL_DOWN
                        ...    message=Unable to login, retry again later.

                    EXCEPT    Format Error    AS    ${err}
                        ${message} =    Catenate
                        ...    Document format is not correct and cannot be uploaded.
                        ...    Correct the format in this work item and try again.
                        ...    Full error message received: ${err}
                        Release Input Work Item     FAILED
                        ...    exception_type=BUSINESS
                        ...    code=DOC_FORMAT_ERROR
                        ...    message=${message}

                    END

        OR

        .. code-block:: python

            from RPA.Robocorp.WorkItems import State, WorkItems

            library = WorkItems()

            def process_and_set_state():
                library.get_input_work_item()
                library.release_input_work_item(State.DONE)
                print(library.current.state)  # would print "State.DONE"

            process_and_set_state()
        """
        # Note that `_auto_release` here is True when automatically releasing items.
        # (internal call)

        last_input = self.inputs[-1] if self.inputs else None
        if not last_input:
            if _auto_release:
                # Have nothing to release and that's normal (reserving for the first
                # time).
                return
            raise RuntimeError(
                "Can't release without reserving first an input work item"
            )
        if last_input.state is not None:
            if _auto_release:
                # Item already released and that's normal when reaching an empty queue
                # and we ask for another item again. We don't want to set states twice.
                return
            raise RuntimeError("Input work item already released")
        assert last_input.parent_id is None, "set state on output item"
        assert last_input.id is not None, "set state on input item with null ID"

        # RF automatically converts string "DONE" to State.DONE object if only `State`
        #  type annotation is used in the keyword definition.
        if not isinstance(state, State):
            # But since we support strings as well now, to stay compatible with Python
            #  behaviour, a "COMPLETE" value is expected instead of "DONE".
            state: str = state.upper()
            state: str = State.DONE.value if state == "DONE" else state
            state: State = State(state)
        exception = None
        if state is State.FAILED:
            if exception_type:
                exception_type: Error = (
                    exception_type
                    if isinstance(exception_type, Error)
                    else Error(exception_type.upper())
                )
                exception = {
                    "type": exception_type.value,
                    "code": code,
                    "message": message,
                }
            elif code or message:
                exc_types = ", ".join(list(Error.__members__))
                raise RuntimeError(f"Must specify failure type from: {exc_types}")

        self.adapter.release_input(last_input.id, state, exception=exception)
        last_input.state = state

    def get_current_work_item(self) -> WorkItem:
        """Get the currently active work item.

        The current work item is used as the target by other keywords
        in this library.

        Keywords ``Get Input Work Item`` and ``Create Output Work Item``
        set the active work item automatically, and return the created
        instance.

        With this keyword the active work item can be retrieved manually.

        Example:

        .. code-block:: robotframework

            *** Tasks ***
            Example task
                ${input} =    Get Current Work Item
                ${output} =   Create Output Work Item
                Set Current Work Item    ${input}
        """
        return self.current


class _WorkItemsSingleton:
    _workItems_intance: Optional[_WorkItemsLibrary] = None

    def __init__(self):
        raise RuntimeError("Call instance() instead")

    @classmethod
    def instance(
        cls,
        autoload: bool = True,
        root: Optional[str] = None,
        default_adapter: Union[Type[BaseAdapter], str] = RobocorpAdapter,
        # pylint: disable=dangerous-default-value
        auto_parse_email: AUTO_PARSE_EMAIL_TYPE = AUTO_PARSE_EMAIL_DEFAULT,
    ) -> _WorkItemsLibrary:
        if cls._workItems_intance is None:
            cls._workItems_intance = _WorkItemsLibrary(
                autoload, root, default_adapter, auto_parse_email
            )
        return cls._workItems_intance
