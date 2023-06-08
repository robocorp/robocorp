import copy
import fnmatch
import json
import logging
import os
from glob import glob
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ._adapters import BaseAdapter
from ._exceptions import ApplicationException, BusinessException, to_exception_type
from ._types import Email, ExceptionType, JSONType, PathType, State
from ._utils import truncate

LOGGER = logging.getLogger(__name__)


class Input:
    def __init__(self, item_id: str, adapter: BaseAdapter):
        self._adapter = adapter
        self._id = item_id
        self._payload: JSONType = self._adapter.load_payload(self.id)
        self._files: List[str] = self._adapter.list_files(self.id)
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

    def email(
        self,
        html=True,
        encoding="utf-8",
        ignore_errors=False,
    ) -> Optional[Email]:
        email = self._parse_email()
        if email is None:
            raise ValueError("No email in work item")

        if email.errors and not ignore_errors:
            raise ValueError("\n".join(email.errors))

        if html and "__mail.html" in self._files:
            content = self._adapter.get_file(self.id, "__mail.html")
            email.html = content.decode(encoding)

        return email

    def _parse_email(self) -> Optional[Email]:
        if not isinstance(self._payload, dict):
            return None

        # Email was successfully parsed by Control Room
        if "email" in self._payload:
            try:
                fields = self._payload["email"]
                email = Email.from_dict(fields)  # type: ignore
                return email
            except Exception as exc:
                LOGGER.warning("Malformed 'email' field: %s", exc)

        # Email parsing by Control Room failed (payload or attachments too big)
        if "failedEmail" in self._payload:
            try:
                fields = self._payload["failedEmail"]
                email = Email.from_dict(fields)  # type: ignore
                email.errors = self._parse_email_errors(self._payload)
                return email
            except Exception as exc:
                LOGGER.warning("Malformed 'failedEmail' field: %s", exc)

        return None

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
        else:
            path = Path(path)

        path.mkdir(parents=True, exist_ok=True)

        paths = []
        for name in self.files:
            if not fnmatch.fnmatch(name, pattern):
                continue

            filepath = (path / name).absolute()
            paths.append(filepath)

            content = self._adapter.get_file(self._id, name)
            with open(filepath, "wb") as fd:
                fd.write(content)

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
            LOGGER.warning('File with name "%s" already exists', name)

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
