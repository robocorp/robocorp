import json
import logging
import os
from pathlib import Path
from typing import Any, Literal, Optional, Union

from robocorp.workitems._exceptions import EmptyQueue
from robocorp.workitems._types import State
from robocorp.workitems._utils import JSONType, json_dumps, resolve_path

from ._base import BaseAdapter

SourceType = Union[Literal["input"], Literal["output"]]
WorkItem = dict[str, Any]

UNDEFINED = object()  # Undefined default value
ENCODING = "utf-8"
LOGGER = logging.getLogger(__name__)

INPUT_HELP = """\
Work items input path not defined, to simulate different input values set the
environment variable `RC_WORKITEM_INPUT_PATH`.

Generated input path: {path}
"""

OUTPUT_HELP = """\
Work items output path not defined, to control the path of the
generated output file set the environment variable `RC_WORKITEM_OUTPUT_PATH`.

Generated output path: {path}
"""


def _show_input_help(path: Path):
    LOGGER.warning(INPUT_HELP.format(path=path), stacklevel=2)


def _show_output_help(path: Path):
    LOGGER.warning(OUTPUT_HELP.format(path=path), stacklevel=2)


class FileAdapter(BaseAdapter):
    """Adapter for simulating work item input queues.

    Uses a local JSON file to test different queue values locally before
    the project is deploying into Control Room.

    If no input or output path is defined by the environment variables
    described below, a path is automatically generated. Additionally,
    the input queue will be populated with an empty work item, as
    Control Room runs will always have at least one input work item.

    Reads and writes all work item files from/to the same parent
    folder as the given input or outputs database.

    Optional environment variables:

    * RC_WORKITEM_INPUT_PATH:  Path to work items input database file
    * RC_WORKITEM_OUTPUT_PATH:  Path to work items output database file

    lazydocs: ignore
    """

    def __init__(self) -> None:
        self._input_path: Optional[Path] = None
        self._output_path: Optional[Path] = None

        self._inputs: list[WorkItem] = self._load_inputs()
        self._outputs: list[WorkItem] = []
        self._releases: dict[str, tuple[State, Optional[dict]]] = {}
        self._index: int = 0

    @property
    def input_path(self):
        if self._input_path is None:
            self._input_path = self._resolve_input_path()

        return self._input_path

    @property
    def output_path(self) -> Path:
        if self._output_path is None:
            self._output_path = self._resolve_output_path()

        return self._output_path

    def _load_inputs(self) -> list[WorkItem]:
        try:
            with open(self.input_path, "r", encoding=ENCODING) as infile:
                data = json.load(infile)

            if not isinstance(data, list):
                raise ValueError("Expected list of items")

            if any(not isinstance(d, dict) for d in data):
                raise ValueError("Items should be dictionaries")

            if len(data) == 0:
                raise ValueError("Expected at least one item")

            return data
        except Exception as exc:
            raise ValueError(f"Invalid work items file: {exc}") from exc

    def _resolve_input_path(self) -> Path:
        env = os.getenv("RC_WORKITEM_INPUT_PATH") or os.getenv(
            "RPA_INPUT_WORKITEM_PATH"
        )

        if env:
            path = resolve_path(env)
        else:
            parent = resolve_path(os.getenv("ROBOT_ARTIFACTS") or "output")
            path = parent / "work-items-in" / "workitems.json"
            _show_input_help(path)

            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding=ENCODING) as fd:
                fd.write(json_dumps([{"payload": None, "files": {}}]))

        return path

    def _save_inputs(self):
        self.input_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.input_path, "w", encoding=ENCODING) as fd:
            fd.write(json_dumps(self._inputs, indent=4))

        LOGGER.info("Saved input work items: %s", self.input_path)

    def _resolve_output_path(self) -> Path:
        env = os.getenv("RC_WORKITEM_OUTPUT_PATH") or os.getenv(
            "RPA_OUTPUT_WORKITEM_PATH"
        )

        if env:
            path = resolve_path(env)
        else:
            parent = resolve_path(os.getenv("ROBOT_ARTIFACTS") or "output")
            path = parent / "work-items-out" / "workitems.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            _show_output_help(path)

        return path

    def _save_outputs(self):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_path, "w", encoding=ENCODING) as fd:
            fd.write(json_dumps(self._outputs, indent=4))

        LOGGER.info("Saved output work items: %s", self.output_path)

    def _get_item(self, item_id: str) -> tuple[SourceType, WorkItem]:
        # The work item ID is analogue to inputs/outputs list queues index
        idx = int(item_id)
        if idx < len(self._inputs):
            return "input", self._inputs[idx]

        if idx < (len(self._inputs) + len(self._outputs)):
            return "output", self._outputs[idx - len(self._inputs)]

        raise ValueError(f"Unknown work item ID: {item_id}")

    # Base class methods:

    def reserve_input(self) -> str:
        if self._index >= len(self._inputs):
            raise EmptyQueue("No work items in the input queue")

        try:
            return str(self._index)
        finally:
            self._index += 1

    def release_input(
        self,
        item_id: str,
        state: State,
        exception: Optional[dict] = None,
    ):
        if item_id in self._releases:
            raise ValueError("Work item already released")

        self._releases[item_id] = (state, exception)
        LOGGER.info(
            "Releasing item %r with %s state and exception: %s",
            item_id,
            state.value,
            exception,
        )

    def create_output(self, parent_id: str, payload: Optional[JSONType] = None) -> str:
        source, _ = self._get_item(parent_id)
        if source != "input":
            raise ValueError(f"Work item parent ({parent_id}) must be an input")
        if parent_id in self._releases:
            raise ValueError(f"Work item parent ({parent_id}) already released")

        item: WorkItem = {"payload": payload, "files": {}}

        self._outputs.append(item)
        self._save_outputs()

        item_id = str(len(self._inputs) + len(self._outputs) - 1)
        return item_id

    def load_payload(self, item_id: str) -> JSONType:
        _, item = self._get_item(item_id)
        return item.get("payload", None)

    def save_payload(self, item_id: str, payload: JSONType):
        source, item = self._get_item(item_id)
        item["payload"] = payload

        if source == "input":
            self._save_inputs()
        else:
            self._save_outputs()

    def list_files(self, item_id: str) -> list[str]:
        _, item = self._get_item(item_id)
        files = item.get("files", {})
        return list(files.keys())

    def get_file(self, item_id: str, name: str) -> bytes:
        source, item = self._get_item(item_id)

        files = item.get("files", {})
        path = files[name]

        if not Path(path).is_absolute():
            if source == "input":
                path = self.input_path.parent / path
            else:
                path = self.output_path.parent / path

        with open(path, "rb") as fd:
            return fd.read()

    def add_file(self, item_id: str, name: str, content: bytes):
        source, item = self._get_item(item_id)

        files = item.setdefault("files", {})
        files[name] = name

        if source == "input":
            path = self.input_path.parent / name
        else:
            path = self.output_path.parent / name

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as fd:
            fd.write(content)

        LOGGER.info("Created file: %s", path)

        if source == "input":
            self._save_inputs()
        else:
            self._save_outputs()

    def remove_file(self, item_id: str, name: str):
        source, item = self._get_item(item_id)

        files = item.get("files", {})
        path = files[name]

        # Note: Doesn't actually remove the file from disk
        LOGGER.info("Would remove file: %s", path)
        del files[name]

        if source == "input":
            self._save_inputs()
        else:
            self._save_outputs()
