import logging
from typing import Any, Optional

from robocorp.workitems._exceptions import EmptyQueue
from robocorp.workitems._requests import Requests
from robocorp.workitems._types import State
from robocorp.workitems._utils import JSONType, required_env, url_join

from ._base import BaseAdapter

UNDEFINED = object()  # Undefined default value
ENCODING = "utf-8"
LOGGER = logging.getLogger(__name__)


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

    lazydocs: ignore
    """

    def __init__(self) -> None:
        # IDs identifying the current robot run and its input.
        self._workspace_id: str = required_env("RC_WORKSPACE_ID")
        self._process_run_id: str = required_env("RC_PROCESS_RUN_ID")
        self._step_run_id: str = required_env("RC_ACTIVITY_RUN_ID")
        self._initial_item_id: Optional[str] = required_env("RC_WORKITEM_ID")

        self._workitem_requests = self._init_workitem_requests()
        self._process_requests = self._init_process_requests()

    def _init_workitem_requests(self) -> Requests:
        # Endpoint for old work items API.
        workitem_host = required_env("RC_API_WORKITEM_HOST")
        workitem_token = required_env("RC_API_WORKITEM_TOKEN")
        route_prefix = (
            url_join(
                workitem_host,
                "json-v1",
                "workspaces",
                self._workspace_id,
                "workitems",
            )
            + "/"
        )
        default_headers = {
            "Authorization": f"Bearer {workitem_token}",
            "Content-Type": "application/json",
        }
        LOGGER.info("Work item API route prefix: %s", route_prefix)
        return Requests(route_prefix, default_headers=default_headers)

    def _init_process_requests(self) -> Requests:
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
        LOGGER.info("Process API route prefix: %s", route_prefix)
        return Requests(route_prefix, default_headers=default_headers)

    def _pop_item(self):
        # Get the next input work item from the cloud queue.
        url = url_join(
            "runs",
            self._process_run_id,
            "robotRuns",
            self._step_run_id,
            "reserve-next-work-item",
        )
        LOGGER.info("Reserving new input work item from: %s", url)
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
        body: dict[str, Any] = {"workItemId": item_id, "state": state.value}
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

        log_func = LOGGER.error if state == State.FAILED else LOGGER.info
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

        LOGGER.info("Creating output item: %s", url)
        response = self._process_requests.post(url, json=body)
        return response.json()["id"]

    def load_payload(self, item_id: str) -> JSONType:
        url = url_join(item_id, "data")

        def handle_error(resp):
            # NOTE: The API might return 404 if no payload is attached to the work
            # item.
            if not (resp.ok or resp.status_code == 404):
                self._workitem_requests.handle_error(resp)

        LOGGER.info("Loading work item payload from: %s", url)
        response = self._workitem_requests.get(url, _handle_error=handle_error)
        return response.json() if response.ok else {}

    def save_payload(self, item_id: str, payload: JSONType):
        url = url_join(item_id, "data")

        LOGGER.info("Saving work item payload to: %s", url)
        self._workitem_requests.put(url, json=payload)

    def list_files(self, item_id: str) -> list[str]:
        url = url_join(item_id, "files")

        LOGGER.info("Listing work item files at: %s", url)
        response = self._workitem_requests.get(url)

        return [item["fileName"] for item in response.json()]

    def get_file(self, item_id: str, name: str) -> bytes:
        # Robocorp API returns URL for S3 download.
        file_id = self.file_id(item_id, name)
        url = url_join(item_id, "files", file_id)

        LOGGER.info("Downloading work item file at: %s", url)
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

    def add_file(self, item_id: str, name: str, content: bytes):
        # Robocorp API returns pre-signed POST details for S3 upload.
        url = url_join(item_id, "files")
        body = {"fileName": str(name), "fileSize": len(content)}
        LOGGER.info(
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
            names = ", ".join(item["fileName"] for item in files)
            raise FileNotFoundError(f"File with name '{name}' not in: {names}")

        # Duplicate filenames should never exist,
        # but use last item just in case
        return matches[-1]["fileId"]
