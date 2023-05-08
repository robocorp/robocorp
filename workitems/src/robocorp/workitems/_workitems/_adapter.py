import json
import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from robocorp.workitems._workitems._types import State
from robocorp.workitems._workitems._utils import (
    JSONType,
    Requests,
    deprecation,
    json_dumps,
    required_env,
    resolve_path,
    url_join,
)

UNDEFINED = object()  # Undefined default value
ENCODING = "utf-8"


class EmptyQueue(IndexError):
    """Raised when trying to load an input item and none available."""


class BaseAdapter(ABC):
    """Abstract base class for work item adapters."""

    @abstractmethod
    def reserve_input(self) -> str:
        """Get next work item ID from the input queue and reserve it."""
        raise NotImplementedError

    @abstractmethod
    def release_input(
        self, item_id: str, state: State, exception: Optional[dict] = None
    ):
        """Release the lastly retrieved input work item and set state."""
        raise NotImplementedError

    @abstractmethod
    def create_output(self, parent_id: str, payload: Optional[JSONType] = None) -> str:
        """Create new output for work item, and return created ID."""
        raise NotImplementedError

    @abstractmethod
    def load_payload(self, item_id: str) -> JSONType:
        """Load JSON payload from work item."""
        raise NotImplementedError

    @abstractmethod
    def save_payload(self, item_id: str, payload: JSONType):
        """Save JSON payload to work item."""
        raise NotImplementedError

    @abstractmethod
    def list_files(self, item_id: str) -> List[str]:
        """List attached files in work item."""
        raise NotImplementedError

    @abstractmethod
    def get_file(self, item_id: str, name: str) -> bytes:
        """Read file's contents from work item."""
        raise NotImplementedError

    @abstractmethod
    def add_file(self, item_id: str, name: str, *, original_name: str, content: bytes):
        """Attach file to work item."""
        raise NotImplementedError

    @abstractmethod
    def remove_file(self, item_id: str, name: str):
        """Remove attached file from work item."""
        raise NotImplementedError


class RobocorpAdapter(BaseAdapter):
    """Adapter for saving/loading work items from Robocorp Control Room.

    Required environment variables:

    * RC_API_WORKITEM_HOST:     Work item API hostname
    * RC_API_WORKITEM_TOKEN:    Work item API access token

    * RC_API_PROCESS_HOST:      Process API hostname
    * RC_API_PROCESS_TOKEN:     Process API access token

    * RC_WORKSPACE_ID:          Control room workspace ID
    * RC_PROCESS_ID:            Control room process ID
    * RC_PROCESS_RUN_ID:        Control room process run ID
    * RC_ROBOT_RUN_ID:          Control room robot run ID

    * RC_WORKITEM_ID:           Control room work item ID (input)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # IDs identifying the current robot run and its input.
        self._workspace_id = required_env("RC_WORKSPACE_ID")
        self._process_run_id = required_env("RC_PROCESS_RUN_ID")
        self._step_run_id = required_env("RC_ACTIVITY_RUN_ID")
        self._initial_item_id: Optional[str] = required_env("RC_WORKITEM_ID")

        self._workitem_requests = self._process_requests = None
        self._init_workitem_requests()
        self._init_process_requests()

    def _init_workitem_requests(self):
        # Endpoint for old work items API.
        workitem_host = required_env("RC_API_WORKITEM_HOST")
        workitem_token = required_env("RC_API_WORKITEM_TOKEN")
        route_prefix = (
            url_join(
                workitem_host, "json-v1", "workspaces", self._workspace_id, "workitems"
            )
            + "/"
        )
        default_headers = {
            "Authorization": f"Bearer {workitem_token}",
            "Content-Type": "application/json",
        }
        logging.info("Work item API route prefix: %s", route_prefix)
        self._workitem_requests = Requests(
            route_prefix, default_headers=default_headers
        )

    def _init_process_requests(self):
        # Endpoint for the new process API.
        process_host = required_env("RC_API_PROCESS_HOST")
        process_token = required_env("RC_API_PROCESS_TOKEN")
        process_id = required_env("RC_PROCESS_ID")
        route_prefix = (
            url_join(
                process_host,
                "process-v1",
                "workspaces",
                self._workspace_id,
                "processes",
                process_id,
            )
            + "/"
        )
        default_headers = {
            "Authorization": f"Bearer {process_token}",
            "Content-Type": "application/json",
        }
        logging.info("Process API route prefix: %s", route_prefix)
        self._process_requests = Requests(route_prefix, default_headers=default_headers)

    def _pop_item(self):
        # Get the next input work item from the cloud queue.
        url = url_join(
            "runs",
            self._process_run_id,
            "robotRuns",
            self._step_run_id,
            "reserve-next-work-item",
        )
        logging.info("Reserving new input work item from: %s", url)
        response = self._process_requests.post(url)
        return response.json()["workItemId"]

    def reserve_input(self) -> str:
        if self._initial_item_id:
            item_id = self._initial_item_id
            self._initial_item_id = None
            return item_id

        item_id = self._pop_item()
        if not item_id:
            raise EmptyQueue("No work items in the input queue")
        return item_id

    def release_input(
        self, item_id: str, state: State, exception: Optional[dict] = None
    ):
        # Release the current input work item in the cloud queue.
        url = url_join(
            "runs",
            self._process_run_id,
            "robotRuns",
            self._step_run_id,
            "release-work-item",
        )
        body = {"workItemId": item_id, "state": state.value}
        if exception:
            for key, value in list(exception.items()):
                # All values are (and should be) strings (if not `None`).
                value = value.strip() if value else value
                if value:
                    exception[key] = value  # keep the stripped string value
                else:
                    # Exclude `None` & empty string values.
                    del exception[key]
            body["exception"] = exception

        log_func = logging.error if state == State.FAILED else logging.info
        log_func(
            "Releasing %s input work item %r into %r with exception: %s",
            state.value,
            item_id,
            url,
            exception,
        )
        self._process_requests.post(url, json=body)

    def create_output(self, parent_id: str, payload: Optional[JSONType] = None) -> str:
        # Putting "output" for the current input work item identified by `parent_id`.
        url = url_join("work-items", parent_id, "output")
        body = {"payload": payload}

        logging.info("Creating output item: %s", url)
        response = self._process_requests.post(url, json=body)
        return response.json()["id"]

    def load_payload(self, item_id: str) -> JSONType:
        url = url_join(item_id, "data")

        def handle_error(resp):
            # NOTE: The API might return 404 if no payload is attached to the work
            # item.
            if not (resp.ok or resp.status_code == 404):
                self._workitem_requests.handle_error(resp)

        logging.info("Loading work item payload from: %s", url)
        response = self._workitem_requests.get(url, _handle_error=handle_error)
        return response.json() if response.ok else {}

    def save_payload(self, item_id: str, payload: JSONType):
        url = url_join(item_id, "data")

        logging.info("Saving work item payload to: %s", url)
        self._workitem_requests.put(url, json=payload)

    def list_files(self, item_id: str) -> List[str]:
        url = url_join(item_id, "files")

        logging.info("Listing work item files at: %s", url)
        response = self._workitem_requests.get(url)

        return [item["fileName"] for item in response.json()]

    def get_file(self, item_id: str, name: str) -> bytes:
        # Robocorp API returns URL for S3 download.
        file_id = self.file_id(item_id, name)
        url = url_join(item_id, "files", file_id)

        logging.info("Downloading work item file at: %s", url)
        response = self._workitem_requests.get(url)
        file_url = response.json()["url"]

        # Perform the actual file download.
        response = self._workitem_requests.get(
            file_url,
            _handle_error=lambda resp: resp.raise_for_status(),
            _sensitive=True,
            headers={},
        )
        return response.content

    def add_file(self, item_id: str, name: str, *, original_name: str, content: bytes):
        # Note that here the `original_name` is useless here. (used with `FileAdapter`
        #   only)
        del original_name

        # Robocorp API returns pre-signed POST details for S3 upload.
        url = url_join(item_id, "files")
        body = {"fileName": str(name), "fileSize": len(content)}
        logging.info(
            "Adding work item file into: %s (name: %s, size: %d)",
            url,
            body["fileName"],
            body["fileSize"],
        )
        response = self._workitem_requests.post(url, json=body)
        data = response.json()

        # Perform the actual file upload.
        url = data["url"]
        fields = data["fields"]
        files = {"file": (name, content)}
        self._workitem_requests.post(
            url,
            _handle_error=lambda resp: resp.raise_for_status(),
            _sensitive=True,
            headers={},
            data=fields,
            files=files,
        )

    def remove_file(self, item_id: str, name: str):
        file_id = self.file_id(item_id, name)
        url = url_join(item_id, "files", file_id)
        self._workitem_requests.delete(url)

    def file_id(self, item_id: str, name: str) -> str:
        url = url_join(item_id, "files")
        response = self._workitem_requests.get(url)

        files = response.json()
        if not files:
            raise FileNotFoundError("No files in work item")

        matches = [item for item in files if item["fileName"] == name]
        if not matches:
            raise FileNotFoundError(
                "File with name '{name}' not in: {names}".format(
                    name=name, names=", ".join(item["fileName"] for item in files)
                )
            )

        # Duplicate filenames should never exist,
        # but use last item just in case
        return matches[-1]["fileId"]


class FileAdapter(BaseAdapter):
    """Adapter for simulating work item input queues.

    Reads inputs from the given database file, and writes
    all created output items into an adjacent file
    with the suffix ``<filename>.output.json``. If the output path is provided by an
    env var explicitly, then the file will be saved with the provided path and name.

    Reads and writes all work item files from/to the same parent
    folder as the given input database.

    Optional environment variables:

    * RPA_INPUT_WORKITEM_PATH:  Path to work items input database file
    * RPA_OUTPUT_WORKITEM_PATH:  Path to work items output database file
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._input_path = UNDEFINED
        self._output_path = UNDEFINED

        self.inputs: List[Dict[str, Any]] = self.load_database()
        self.outputs: List[Dict[str, Any]] = []
        self.index: int = 0

    def _get_item(self, item_id: str) -> Tuple[str, Dict[str, Any]]:
        # The work item ID is analogue to inputs/outputs list queues index.
        idx = int(item_id)
        if idx < len(self.inputs):
            return "input", self.inputs[idx]

        if idx < (len(self.inputs) + len(self.outputs)):
            return "output", self.outputs[idx - len(self.inputs)]

        raise ValueError(f"Unknown work item ID: {item_id}")

    def reserve_input(self) -> str:
        if self.index >= len(self.inputs):
            raise EmptyQueue("No work items in the input queue")

        try:
            return str(self.index)
        finally:
            self.index += 1

    def release_input(
        self, item_id: str, state: State, exception: Optional[dict] = None
    ):
        # Nothing happens for now on releasing local dev input Work Items.
        log_func = logging.error if state == State.FAILED else logging.info
        log_func(
            "Releasing item %r with %s state and exception: %s",
            item_id,
            state.value,
            exception,
        )

    @property
    def input_path(self) -> Optional[Path]:
        if self._input_path is UNDEFINED:
            # pylint: disable=invalid-envvar-default
            old_path = os.getenv("RPA_WORKITEMS_PATH")
            if old_path:
                deprecation(
                    "Work items load - Old path style usage detected, please use the "
                    "'RPA_INPUT_WORKITEM_PATH' env var instead "
                    "(more details under documentation: https://robocorp.com/docs/development-guide/control-room/data-pipeline#developing-with-work-items-locally)"  # noqa: E501
                )
            path = os.getenv("RPA_INPUT_WORKITEM_PATH", default=old_path)
            if path:
                logging.info("Resolving input path: %s", path)
                self._input_path = resolve_path(path)
            else:
                # Will raise `TypeError` during inputs loading and will populate the
                # list with one empty initial input.
                self._input_path = None

        return self._input_path

    @property
    def output_path(self) -> Path:
        if self._output_path is UNDEFINED:
            # This is usually set once per loaded input work item.
            new_path = os.getenv("RPA_OUTPUT_WORKITEM_PATH")
            if new_path:
                self._output_path = resolve_path(new_path)
                self._output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                deprecation(
                    "Work items save - Old path style usage detected, please use the "
                    "'RPA_OUTPUT_WORKITEM_PATH' env var instead "
                    "(more details under documentation: https://robocorp.com/docs/development-guide/control-room/data-pipeline#developing-with-work-items-locally)"  # noqa: E501
                )
                if not self.input_path:
                    raise RuntimeError(
                        "You must provide a path for at least one of the input or "
                        "output work items files"
                    )
                self._output_path = self.input_path.with_suffix(".output.json")

        return self._output_path

    def _save_to_disk(self, source: str) -> None:
        if source == "input":
            if not self.input_path:
                raise RuntimeError(
                    "Can't save an input item without a path defined, use "
                    "'RPA_INPUT_WORKITEM_PATH' env for this matter"
                )
            path = self.input_path
            data = self.inputs
        else:
            path = self.output_path
            data = self.outputs

        with open(path, "w", encoding=ENCODING) as fd:
            fd.write(json_dumps(data, indent=4))

        logging.info("Saved into %s file: %s", source, path)

    def create_output(self, _: str, payload: Optional[JSONType] = None) -> str:
        # Note that the `parent_id` is not used during local development.
        item: Dict[str, Any] = {"payload": payload, "files": {}}
        self.outputs.append(item)

        self._save_to_disk("output")
        return str(len(self.inputs) + len(self.outputs) - 1)  # new output work item ID

    def load_payload(self, item_id: str) -> JSONType:
        _, item = self._get_item(item_id)
        return item.get("payload", {})

    def save_payload(self, item_id: str, payload: JSONType):
        source, item = self._get_item(item_id)
        item["payload"] = payload
        self._save_to_disk(source)

    def list_files(self, item_id: str) -> List[str]:
        _, item = self._get_item(item_id)
        files = item.get("files", {})
        return list(files.keys())

    def get_file(self, item_id: str, name: str) -> bytes:
        source, item = self._get_item(item_id)
        files = item.get("files", {})

        path = files[name]
        if not Path(path).is_absolute():
            parent = (
                self.input_path.parent if source == "input" else self.output_path.parent
            )
            path = parent / path

        with open(path, "rb") as infile:
            return infile.read()

    def add_file(self, item_id: str, name: str, *, original_name: str, content: bytes):
        source, item = self._get_item(item_id)
        files = item.setdefault("files", {})

        parent = (
            self.input_path.parent if source == "input" else self.output_path.parent
        )
        path = parent / original_name  # the file on disk will keep its original name
        with open(path, "wb") as fd:
            fd.write(content)
        logging.info("Created file: %s", path)
        files[name] = original_name  # file path relative to the work item

        self._save_to_disk(source)

    def remove_file(self, item_id: str, name: str):
        source, item = self._get_item(item_id)
        files = item.get("files", {})

        path = files[name]
        logging.info("Would remove file: %s", path)
        # Note that the file doesn't get removed from disk as well.
        del files[name]

        self._save_to_disk(source)

    def load_database(self) -> List:
        try:
            try:
                with open(self.input_path, "r", encoding=ENCODING) as infile:
                    data = json.load(infile)
            except (TypeError, FileNotFoundError):
                logging.warning("No input work items file found: %s", self.input_path)
                data = []

            if isinstance(data, list):
                assert all(
                    isinstance(d, dict) for d in data
                ), "Items should be dictionaries"
                if len(data) == 0:
                    data.append({"payload": {}})
                return data

            # Attempt to migrate from old format
            assert isinstance(data, dict), "Not a list or dictionary"
            deprecation("Work items file as mapping is deprecated")
            workspace = next(iter(data.values()))
            work_item = next(iter(workspace.values()))
            return [{"payload": work_item}]
        except Exception as exc:  # pylint: disable=broad-except
            logging.exception("Invalid work items file because of: %s", exc)
            return [{"payload": {}}]
