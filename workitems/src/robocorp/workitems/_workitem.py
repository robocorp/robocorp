import fnmatch
import json
import logging
import os
import warnings
from glob import glob
from pathlib import Path
from typing import Any, Optional, Union

from ._adapters import BaseAdapter
from ._exceptions import ApplicationException, BusinessException, to_exception_type
from ._types import Email, ExceptionType, JSONType, PathType, State
from ._utils import truncate

LOGGER = logging.getLogger(__name__)


class WorkItem:
    def __init__(
        self,
        adapter: BaseAdapter,
        item_id: Optional[str] = None,
        parent_id: Optional[str] = None,
    ):
        #: API client adpater
        self._adapter = adapter
        #: Current work item ID
        self._id: Optional[str] = item_id
        #: Parent work item ID (output only)
        self._parent_id: Optional[str] = parent_id
        #: Work item payload (JSON)
        self._payload: JSONType = None
        #: Current work item files
        self._files: list[str] = []
        #: Files queued for upload
        self._files_to_add: dict[str, Path] = {}
        #: Files queued for removal
        self._files_to_remove: set[str] = set()
        #: Flag for saved/dirty state
        self._saved = False

    @property
    def id(self) -> Optional[str]:
        """Current ID for work item."""
        return self._id

    @property
    def parent_id(self) -> Optional[str]:
        """Current parent work item ID (output only)."""
        return self._parent_id

    @property
    def payload(self) -> JSONType:
        """Current JSON payload."""
        return self._payload

    @payload.setter
    def payload(self, value: JSONType):
        self._saved = False
        self._payload = value

    @property
    def files(self) -> list[str]:
        """Names of attached files."""
        return self._files

    @property
    def saved(self) -> bool:
        """Is the current item saved."""
        return self._saved

    def load(self) -> None:
        """Load work item payload and file listing from Control Room."""
        if self.id is None:
            raise RuntimeError("Unable to load unsaved item")

        self._payload = self._adapter.load_payload(self.id)
        self._files = self._adapter.list_files(self.id)
        self._files.sort()
        self._saved = True

    def save(self):
        """Save the current work item.

        Updates the work item payload and adds/removes all pending files.
        """
        if self.id is not None:
            self._adapter.save_payload(self.id, payload=self.payload)
        elif self.parent_id is not None:
            self._id = self._adapter.create_output(
                self.parent_id,
                payload=self.payload,
            )
        else:
            raise RuntimeError("Invalid work item state (no id or parent_id)")

        assert self.id is not None

        for name, path in self._files_to_add.items():
            with open(path, "rb") as fd:
                self._adapter.add_file(
                    item_id=self.id,
                    name=name,
                    content=fd.read(),
                )

        for name in self._files_to_remove:
            self._adapter.remove_file(self.id, name)

        self._files = list(
            set(self._files) - set(self._files_to_remove) | set(self._files_to_add)
        )
        self._files.sort()
        self._files_to_add = {}
        self._files_to_remove = set()
        self._saved = True

    def add_file(self, path: Union[Path, str], name: Optional[str] = None) -> Path:
        """Attach a file from the local machine to the work item.

        Note: Files are not uploaded until the item is saved.

        Args:
            path: Path to attached file
            name: Custom name for file in work item

        Returns:
            Resolved path to added file
        """
        path = Path(path).resolve()
        name = name or path.name

        if not path.is_file():
            raise FileNotFoundError(f"Not a valid file: {path}")

        if name in self._files:
            LOGGER.warning('File with name "%s" already exists', name)

        self._saved = False
        self._files_to_add[name] = path
        LOGGER.info("Added file: %s", name)

        return path

    def add_files(self, pattern: str) -> list[Path]:
        """Attach files from the local machine to the work item that
        match the given pattern.

        Note: Files are not uploaded until the item is saved.

        Args:
            pattern: Glob pattern for attached file paths

        Returns:
            List of added paths
        """
        matches = glob(pattern, recursive=False)

        paths = []
        for match in matches:
            path = self.add_file(match)
            paths.append(path)

        LOGGER.info("Added %d file(s)", len(paths))
        return paths

    def remove_file(self, name: str, missing_ok: bool = False):
        """Remove attached file with given name.

        Note: Files are not removed from Control Room until the item is saved.

        Args:
            name: Name of file
            missing_ok: Do nothing if given file does not exist
        """
        if name not in self._files:
            if missing_ok:
                return
            else:
                raise FileNotFoundError(f"No such file in work item: {name}")

        LOGGER.info("Removing file: %s", name)
        self._files_to_remove.add(name)
        self._saved = False

    def remove_files(self, pattern: str) -> list[str]:
        """Remove attached files that match the given pattern.

        Note: Files are not removed from Control Room until the item is saved.

        Args:
            pattern: Glob pattern for file names

        Returns:
            List of matched names
        """
        names = []
        for name in self._files:
            if fnmatch.fnmatch(name, pattern):
                self.remove_file(name)
                names.append(name)

        LOGGER.info("Removing %d file(s)", len(names))
        return names


class Input(WorkItem):
    """Container for an input work item.

    An input work item can contain arbitrary JSON data in the `payload` section,
    and optionally attached files that are stored in Control Room.

    Each step run of a process in Control Room has at least one input
    work item associated with it, but the step's input queue can have
    multiple input items in it.

    There can only be one input work item reserved at a time. To reserve
    the next item, the current item needs to be released as either
    passed or failed.
    """

    def __init__(self, adapter: BaseAdapter, item_id: str):
        super().__init__(adapter, item_id=item_id)
        self._state: Optional[State] = None
        self._outputs: list[Output] = []
        self._saved = True

    def __repr__(self):
        payload = truncate(json.dumps(self._payload), 64)
        return (
            "Input["
            + f"id={self.id},"
            + f"payload={payload},"
            + f"files={self.files},"
            + f"state={self.state},"
            + f"saved={self.saved}]"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.released:
            return False

        if exc_type is None:
            self.done()
            return False

        exception_type = to_exception_type(exc_type)
        code = getattr(exc_value, "code", None)
        message = getattr(exc_value, "message", str(exc_value))

        self.fail(exception_type=exception_type, code=code, message=message)

        # Do not propagate library-specific exceptions
        return any(
            issubclass(exc_type, type_)
            for type_ in (ApplicationException, BusinessException)
        )

    @property
    def state(self) -> Optional[State]:
        """Current release state."""
        return self._state

    @property
    def released(self) -> bool:
        """Is the current item released."""
        return self._state is not None

    @property
    def outputs(self) -> list["Output"]:
        """Child output work items."""
        return list(self._outputs)

    def save(self):
        """Save the current input work item.

        Updates the work item payload and adds/removes all pending files.

        **Note:** Modifying input work items is not recommended, as it will
         make traceability after execution difficult, and potentially make
         the process behave in unexpected ways.
        """
        super().save()

    def email(
        self,
        html=True,
        encoding="utf-8",
        ignore_errors=False,
    ) -> Optional[Email]:
        """Parse an email attachment from the work item.

        Args:
            html: Parse the HTML content into the `html` attribute
            encoding: Text encoding of the email
            ignore_errors: Ignore possible parsing errors from Control Room

        Returns:
            An email container with metadata and content

        Raises:
            ValueError: No email attached or content is malformed
        """
        assert self.id is not None

        email = self._parse_email()

        if email.errors and not ignore_errors:
            raise ValueError("\n".join(email.errors))

        if html and "__mail.html" in self._files:
            content = self._adapter.get_file(self.id, "__mail.html")
            email.html = content.decode(encoding)

        return email

    def _parse_email(self) -> Email:
        if not isinstance(self._payload, dict):
            typename = type(self._payload).__name__
            raise ValueError(f"Expected 'dict' payload, was '{typename}'")

        def _try_parse(fields):
            try:
                email = Email.from_dict(fields)  # type: ignore
                return email
            except KeyError as err:
                raise ValueError(f"Missing key in 'email' field: {err}") from err
            except Exception as err:
                raise ValueError(f"Malformed 'email' field: {err}") from err

        # Email was successfully parsed by Control Room
        if "email" in self._payload:
            fields = self._payload["email"]
            email = _try_parse(fields)
            return email

        # Email parsing by Control Room failed (payload or attachments too big)
        if "failedEmail" in self._payload:
            fields = self._payload["failedEmail"]
            email = _try_parse(fields)
            email.errors = self._parse_email_errors(self._payload)
            return email

        # No email fields in payload
        raise ValueError("No email in work item")

    def _parse_email_errors(self, payload: dict[str, Any]) -> list[str]:
        errors = payload.get("errors", [])
        if not isinstance(errors, list):
            LOGGER.warning("Expected 'errors' as 'list', was '%s'", type(errors))
            return []

        result = []
        for err in errors:
            msg = err["message"]
            if files := err.get("files"):
                names = ", ".join(f["name"] for f in files)
                msg += f" ({names})"
            result.append(msg)

        return result

    def get_file(self, name: str, path: Optional[PathType] = None) -> Path:
        """Download file with given name.

        If a `path` is not defined, uses the Robot root or current working
        directory.

        Args:
            name: Name of file
            path: Path to created file

        Returns:
            Path to created file
        """
        assert self.id is not None

        if name not in self.files:
            raise FileNotFoundError(f"No file with name: {name}")

        if path is None:
            root = os.getenv("ROBOT_ROOT", "")
            path = Path(root) / name
        else:
            path = Path(path)

        content = self._adapter.get_file(self.id, name)
        with open(path, "wb") as fd:
            fd.write(content)

        return path.absolute()

    def get_files(self, pattern: str, path: Optional[Path] = None) -> list[Path]:
        """Download all files attached to this work item that match
        the given pattern.

        If a `path` is not defined, uses the Robot root or current working
        directory.

        Args:
            pattern: Glob pattern for file names
            path: Directory to store files in

        Returns:
            List of created file paths
        """
        assert self.id is not None

        if path is None:
            root = os.getenv("ROBOT_ROOT", "")
            path = Path(root)
        else:
            path = Path(path)

        path.mkdir(parents=True, exist_ok=True)

        paths = []
        for name in self.files:
            if not fnmatch.fnmatch(name, pattern):
                continue

            filepath = (path / name).absolute()
            paths.append(filepath)

            content = self._adapter.get_file(self.id, name)
            with open(filepath, "wb") as fd:
                fd.write(content)

        return paths

    def create_output(self) -> "Output":
        """Create an output work item that is a child of this item."""
        assert self.id is not None

        item = Output(adapter=self._adapter, parent_id=self.id)
        self._outputs.append(item)
        return item

    def done(self):
        """Mark this work item as done, and release it."""
        assert self.id is not None

        if self.state is not None:
            raise RuntimeError("Work item already released")

        state = State.DONE
        self._adapter.release_input(self.id, state, exception=None)
        self._state = state

    def fail(
        self,
        exception_type: Union[ExceptionType, str] = ExceptionType.APPLICATION,
        code: Optional[str] = None,
        message: Optional[str] = None,
    ):
        """Mark this work item as failed, and release it.

        Args:
            exception_type: Type of failure (APPLICATION or BUSINESS)
            code: Custom error code for the failure
            message: Human-readable error message
        """
        assert self.id is not None

        if self.state is not None:
            raise RuntimeError("Work item already released")

        type_ = (
            exception_type
            if isinstance(exception_type, ExceptionType)
            else ExceptionType(exception_type.upper())
        )

        exception = {
            "type": type_.value,
            "code": code,
            "message": message,
        }

        state = State.FAILED
        self._adapter.release_input(self.id, state, exception=exception)
        self._state = state

    # Backwards compatibility
    def download_file(self, name: str, path: Optional[PathType] = None) -> Path:
        """Deprecated method, use `get_file` instead.

        lazydocs: ignore
        """
        warnings.warn(
            "download_file() will be removed in version 2.x, use get_file()",
            DeprecationWarning,
        )
        return self.get_file(name, path)

    def download_files(self, pattern: str, path: Optional[Path] = None) -> list[Path]:
        """Deprecated method, use `get_files` instead.

        lazydocs: ignore
        """
        warnings.warn(
            "download_files() will be removed in version 2.x, use get_files()",
            DeprecationWarning,
        )
        return self.get_files(pattern, path)


class Output(WorkItem):
    """Container for an output work item.

    Created output items are added to an output queue, and released
    to the next step of a process when the current run ends.

    Note: An output item always has an input item as a parent,
    which is used for traceability in a work item's history.
    """

    def __init__(self, adapter: BaseAdapter, parent_id: str):
        super().__init__(adapter, parent_id=parent_id)

    def __repr__(self):
        payload = truncate(str(self.payload), 64)
        return (
            "Output["
            + f"id={self.id},"
            + f"parent={self.parent_id},"
            + f"payload={payload},"
            + f"files={self.files},"
            + f"saved={self.saved}]"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.save()
