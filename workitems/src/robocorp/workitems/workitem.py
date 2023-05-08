import copy
import fnmatch
import logging
import os
from pathlib import Path
from shutil import copy2
from typing import Dict, List, Optional, Union

from robocorp.workitems._workitems._adapter import BaseAdapter
from robocorp.workitems._workitems._types import Error, State
from robocorp.workitems._workitems._utils import JSONType, is_json_equal, truncate


# TODO: Split into input and output items
class WorkItem:
    """Base class for input and output work items.

    Args:
        adapter:   Adapter instance
        item_id:   Work item ID (optional)
        parent_id: Parent work item's ID (optional)

    """

    def __init__(
        self,
        adapter: BaseAdapter,
        item_id: Optional[str] = None,
        parent_id: Optional[str] = None,
    ):
        #: Adapter for loading/saving content
        self.adapter = adapter
        #: This item's and/or parent's ID
        self.id: Optional[str] = item_id
        self.parent_id: Optional[str] = parent_id
        assert self.id is not None or self.parent_id is not None
        #: Item's state on release; can be set once
        self.state: Optional[State] = None
        #: Remote JSON payload, and queued changes
        self._payload: JSONType = {}
        self._payload_cache: JSONType = {}
        #: Remote attached files, and queued changes
        self._files: List[str] = []
        self._files_to_add: Dict[str, Path] = {}
        self._files_to_remove: List[str] = []

    def __repr__(self):
        payload = truncate(str(self.payload), 64)
        files = len(self.files)
        return f"WorkItem(id={self.id}, payload={payload}, files={files}, state={self.state})"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.fail(message=str(exc_value))
        else:
            self.done()

    @property
    def is_dirty(self):
        """Check if work item has unsaved changes."""
        return (
            self.id is None
            or not is_json_equal(self._payload, self._payload_cache)
            or self._files_to_add
            or self._files_to_remove
        )

    @property
    def payload(self):
        return self._payload_cache

    @payload.setter
    def payload(self, value):
        self._payload_cache = value

    @property
    def files(self):
        """List of filenames, including local files pending upload and
        excluding files pending removal.
        """
        current = [item for item in self._files if item not in self._files_to_remove]
        current.extend(self._files_to_add)
        return list(sorted(set(current)))

    @property
    def released(self):
        return self.state is not None

    def load(self):
        """Load data payload and list of files."""
        self._payload = self.adapter.load_payload(self.id)
        self._payload_cache = copy.deepcopy(self._payload)

        self._files = self.adapter.list_files(self.id)
        self._files_to_add = {}
        self._files_to_remove = []

    def save(self):
        """Save data payload and attach/remove files."""
        if self.id is None:
            self.id = self.adapter.create_output(self.parent_id, payload=self.payload)
        else:
            self.adapter.save_payload(self.id, self.payload)

        for name in self._files_to_remove:
            self.adapter.remove_file(self.id, name)

        for name, path in self._files_to_add.items():
            with open(path, "rb") as infile:
                self.adapter.add_file(
                    self.id, name, original_name=path.name, content=infile.read()
                )

        # Empty unsaved values
        self._payload = self._payload_cache
        self._payload_cache = copy.deepcopy(self._payload)

        self._files = self.files
        self._files_to_add = {}
        self._files_to_remove = []

    def get_file(self, name, path=None) -> str:
        """Load an attached file and store it on the local filesystem.

        :param name: Name of attached file
        :param path: Destination path. Default to current working directory.
        :returns:    Path to created file
        """
        if name not in self.files:
            raise FileNotFoundError(f"No such file: {name}")

        if not path:
            root = os.getenv("ROBOT_ROOT", "")
            path = os.path.join(root, name)

        if name in self._files_to_add:
            local_path = self._files_to_add[name]
            if Path(local_path).resolve() != Path(path).resolve():
                copy2(local_path, path)
        else:
            content = self.adapter.get_file(self.id, name)
            with open(path, "wb") as outfile:
                outfile.write(content)

        # Always return absolute path
        return str(Path(path).resolve())

    # TODO: implement file pattern get
    def get_files(self, pattern, dirname=None) -> List[str]:
        paths = []
        for name in self.files:
            if fnmatch.fnmatch(name, pattern):
                if dirname:
                    path = self.get_file(name, os.path.join(dirname, name))
                else:
                    path = self.get_file(name)
                paths.append(path)

        logging.info("Downloaded %d file(s)", len(paths))
        return paths

    def add_file(self, path, name=None):
        """Add file to current work item. Does not upload
        until ``save()`` is called.

        :param path: Path to file to upload
        :param name: Name of file in work item. If not given,
                     name of file on disk is used.
        """
        path = Path(path).resolve()

        if path in self._files_to_add.values():
            logging.warning("File already added: %s", path)

        if not path.is_file():
            raise FileNotFoundError(f"Not a valid file: {path}")

        name = name or path.name
        self._files_to_add[name] = path

        if name in self._files_to_remove:
            self._files_to_remove.remove(name)

        return name

    def remove_file(self, name, missing_ok=True):
        """Remove file from current work item. Change is not applied
        until ``save()`` is called.

        :param name: Name of attached file
        """
        if not missing_ok and name not in self.files:
            raise FileNotFoundError(f"No such file: {name}")

        if name in self._files:
            self._files_to_remove.append(name)

        if name in self._files_to_add:
            del self._files_to_add[name]

        return name

    def create_output(
        self,
        variables: Optional[dict] = None,
        files: Optional[Union[str, List[str]]] = None,
        save: bool = True,
    ):
        # TODO: Implement
        raise NotImplementedError

    def _ensure_releasable(self):
        # TODO: Move these checks elsewhere
        if self.state is not None:
            raise RuntimeError("Input work item already released")
        if self.parent_id is not None:
            raise RuntimeError("Cannot set state on output item")
        if self.id is None:
            raise RuntimeError("Cannot set state on input item with null ID")

    def done(self):
        """Mark item status as DONE."""
        self._ensure_releasable()

        state = State.DONE

        self.adapter.release_input(self.id, state, exception=None)
        self.state = state

    def fail(
        self,
        exception_type: Union[Error, str] = Error.APPLICATION,
        code: Optional[str] = None,
        message: Optional[str] = None,
    ):
        self._ensure_releasable()
        state = State.FAILED

        type_ = (
            exception_type
            if isinstance(exception_type, Error)
            else Error(exception_type.upper())
        )
        exception = {
            "type": type_.value,
            "code": code,
            "message": message,
        }

        self.adapter.release_input(self.id, state, exception=exception)
        self.state = state
