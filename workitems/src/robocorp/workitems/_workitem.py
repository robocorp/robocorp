import copy
import fnmatch
import json
import logging
import os
import warnings
from glob import glob
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml

from ._adapters import BaseAdapter
from ._email import parse_email_body
from ._exceptions import ApplicationException, BusinessException, to_exception_type
from ._types import ExceptionType, JSONType, PathType, State
from ._utils import truncate

WorkItem = Union["Input", "Output"]

LOGGER = logging.getLogger(__name__)

EMAIL_DEPRECATION_MESSAGE = (
    "Legacy non-parsed e-mail trigger detected! Please enable "
    '"Parse email" configuration option in Control Room. (more'
    " details: https://robocorp.com/docs/control-room/attended"
    "-or-unattended/email-trigger#parse-email)"
)


class Input:
    def __init__(self, item_id: str, adapter: BaseAdapter):
        self._adapter = adapter
        self._id = item_id
        self._payload: JSONType = self._adapter.load_payload(self.id)
        self._files: List[str] = self._adapter.list_files(self.id)
        self._email: Optional[str] = None
        self._state: Optional[State] = None
        self._outputs: list[Output] = []

    def __repr__(self):
        payload = truncate(json.dumps(self._payload), 64)
        return (
            "Input["
            + f"id={self._id},"
            + f"payload={payload},"
            + f"files={self._files},"
            + f"state={self._state}]"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            exception_type = to_exception_type(exc_type)
            self.fail(exception_type=exception_type, message=str(exc_value))
        else:
            self.done()

        # Do not propagate library-specific exceptions
        return exc_type in (ApplicationException, BusinessException)

    @property
    def id(self):
        return self._id

    @property
    def payload(self):
        return copy.deepcopy(self._payload)

    @property
    def files(self):
        return list(self._files)

    @property
    def state(self):
        return self._state

    @property
    def released(self):
        return self._state is not None

    @property
    def outputs(self):
        return list(self._outputs)

    def email(self) -> Optional[JSONType]:
        if self._email is not None:
            return self._email

        body = self._email_body()
        if body is None:
            return None

        try:
            return json.loads(body)
        except Exception as exc:
            LOGGER.debug("E-mail body not valid JSON: %s", exc)

        try:
            return yaml.full_load(body)
        except Exception as exc:
            LOGGER.debug("E-mail body not valid YAML: %s", exc)        

        return body

    def _email_body(self) -> Optional[str]:
        if not isinstance(self._payload, dict):
            return None

        if "email" in self._payload:
            content = self._payload["email"]
            if isinstance(content, dict) and "body" in content:
                return content["body"]

        if "__mail.html" in self._files:
            content = self._adapter.get_file(self.id, "__mail.html")
            return content.decode("utf-8")

        if "rawEmail" in self._payload:
            content = self._payload["rawEmail"]
            if isinstance(content, str):
                warnings.warn(
                    EMAIL_DEPRECATION_MESSAGE, DeprecationWarning, stacklevel=2
                )
                body, _ = parse_email_body(content)
                return body

        return None

    def download_file(self, name: str, path: Optional[PathType] = None) -> Path:
        if name not in self.files:
            raise KeyError(name)

        if path is None:
            root = os.getenv("ROBOT_ROOT", "")
            path = Path(root) / name
        else:
            path = Path(path)

        content = self._adapter.get_file(self.id, name)
        with open(path, "wb") as fd:
            fd.write(content)

        return path.absolute()

    def download_files(self, pattern: str, path: Optional[Path] = None) -> List[Path]:
        if path is None:
            root = os.getenv("ROBOT_ROOT", "")
            path = Path(root)

        path.mkdir(parents=True, exist_ok=True)

        paths = []
        for name in self.files:
            if fnmatch.fnmatch(name, pattern):
                content = self._adapter.get_file(self._id, name)
                with open(path, "wb") as fd:
                    fd.write(content)
                paths.append(path.absolute())

        return paths

    def create_output(self) -> "Output":
        item = Output(parent_id=self.id, adapter=self._adapter)
        self._outputs.append(item)
        return item

    def done(self):
        if self._state is not None:
            raise RuntimeError("Work item already released")

        state = State.DONE
        self._adapter.release_input(self._id, state, exception=None)
        self._state = state

    def fail(
        self,
        exception_type: Union[ExceptionType, str] = ExceptionType.APPLICATION,
        code: Optional[str] = None,
        message: Optional[str] = None,
    ):
        if self._state is not None:
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
        self._adapter.release_input(self._id, state, exception=exception)
        self._state = state


class Output:
    def __init__(self, parent_id: str, adapter: BaseAdapter):
        self._adapter = adapter
        self._parent_id = parent_id
        self._id: Optional[str] = None
        self._payload: JSONType = {}
        self._files: Dict[str, Path] = {}

    def __repr__(self):
        payload = truncate(str(self.payload), 64)
        return (
            "Output["
            + f"parent={self._parent_id},"
            + f"payload={payload},"
            + f"files={self.files},"
            + f"saved={self.saved}]"
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.save()

    @property
    def id(self):
        return self._id

    @property
    def parent_id(self):
        return self._parent_id

    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, value):
        self._payload = value

    @property
    def files(self):
        return list(self._files.keys())

    @property
    def saved(self):
        return self._id is not None

    def save(self):
        if self.saved:
            raise RuntimeError("Output already saved")

        self._id = self._adapter.create_output(self.parent_id, payload=self.payload)

        for name, path in self._files.items():
            with open(path, "rb") as fd:
                self._adapter.add_file(
                    self._id,
                    name,
                    original_name=path.name,
                    content=fd.read(),
                )

    def add_file(self, path: Union[Path, str], name: Optional[str] = None) -> Path:
        path = Path(path).resolve()
        name = name or path.name

        if not path.is_file():
            raise FileNotFoundError(f"Not a valid file: {path}")

        if name in self._files:
            LOGGER.warning(f'File with name "{name}" already exists')

        self._files[name] = path
        return path

    def add_files(self, pattern: str) -> list[Path]:
        matches = glob(pattern, recursive=False)

        paths = []
        for match in matches:
            path = self.add_file(match)
            paths.append(path)

        LOGGER.info("Added %d file(s)", len(paths))
        return paths
