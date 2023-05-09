import importlib
import json
import logging
import os
import random
import time
import urllib.parse as urlparse
import warnings
from email.header import decode_header  # pylint: disable=E0611
from email.message import Message  # pylint: disable=E0611
from json import JSONDecodeError  # pylint: disable=no-name-in-module
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import requests
from requests.exceptions import HTTPError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

# Sentinel value for undefined argument
UNDEFINED = object()

JSONType = Union[Dict[str, Any], List[Any], str, int, float, bool, None]
PathType = Union[Path, str]

DEBUG_ON = bool(os.getenv("RPA_DEBUG_API"))

ENCODING = "utf-8"


def required_env(name: str, default: Any = UNDEFINED) -> str:
    """Load required environment variable.

    Args:
        name: Name of environment variable
        default: Value to use if variable is undefined.
                    If not given and variable is undefined, raises KeyError.

    """
    val = os.getenv(name, default)
    if val is UNDEFINED:
        raise KeyError(f"Missing required environment variable: {name}")
    return val


def import_by_name(name: str, caller: Optional[str] = None) -> Any:
    """Import module (or attribute) by name.

    Args:
        name: Import path, e.g. RPA.Robocorp.WorkItems.RobocorpAdapter
        caller: Caller file name

    """
    name = str(name)

    # Attempt import as path module
    try:
        return importlib.import_module(name)
    except ImportError:
        pass

    # Attempt import from calling file
    if caller is not None:
        try:
            module = importlib.import_module(caller)
            return getattr(module, name)
        except AttributeError:
            pass

    # Attempt import as path to attribute inside module
    if "." in name:
        try:
            path, attr = name.rsplit(".", 1)
            module = importlib.import_module(path)
            return getattr(module, attr)
        except (AttributeError, ImportError):
            pass

    raise ValueError(f"No module/attribute with name: {name}")


def resolve_path(path: str) -> Path:
    """Resolve a string-based path, and replace variables."""
    return Path(path).expanduser().resolve()


def url_join(*parts):
    """Join parts of URL and handle missing/duplicate slashes."""
    return "/".join(str(part).strip("/") for part in parts)


def json_dumps(payload: JSONType, **kwargs):
    """Create JSON string in UTF-8 encoding."""
    kwargs.setdefault("ensure_ascii", False)
    return json.dumps(payload, **kwargs)


def is_json_equal(left: JSONType, right: JSONType):
    """Deep-compare two output JSONs."""
    return json_dumps(left, sort_keys=True) == json_dumps(right, sort_keys=True)


def truncate(text: str, size: int):
    """Truncate a string from the middle."""
    if len(text) <= size:
        return text

    ellipsis = " ... "
    segment = (size - len(ellipsis)) // 2
    return text[:segment] + ellipsis + text[-segment:]


# TODO: Move logging functions to a proper place
def deprecation(message):
    """Emits once a deprecation warning log given the provided `message`."""
    logging.captureWarnings(True)
    try:
        warnings.warn(message, FutureWarning, stacklevel=2)
    finally:
        logging.captureWarnings(False)


def log_more(message, *args, func=logging.debug):
    func(message, *args)
    if DEBUG_ON:
        logging.debug(str(message) % args)


def get_dot_value(source: Dict, key: str) -> Any:
    """Returns the end value from `source` dictionary given `key` traversal."""
    keys = key.split(".")
    value = source
    for _key in keys:
        value = value.get(_key)
    return value


def set_dot_value(source: Dict, key: str, *, value: Any):
    """Sets the end `value` into `source` dictionary given `key` destination."""
    keys = key.rsplit(".", 1)  # one or at most two parts
    if len(keys) == 2:
        source = get_dot_value(source, keys[0])
    source[keys[-1]] = value


def _needs_retry(exc: BaseException) -> bool:
    # Don't retry on some specific error codes or messages.

    # https://www.restapitutorial.com/httpstatuscodes.html
    # 400 - payload is bad and needs to be changed
    # 401 - missing auth bearer token
    # 403 - auth is in place, but not allowed (insufficient privileges)
    # 409 - payload not good for the affected resource
    no_retry_codes = [400, 401, 403, 409]
    no_retry_messages = []

    if isinstance(exc, RequestsHTTPError):
        if exc.status_code in no_retry_codes or exc.status_message in no_retry_messages:
            return False

        if exc.status_code == 429:
            # We hit the rate limiter, so sleep extra.
            seconds = random.uniform(1, 3)
            log_more("Rate limit hit, sleeping: %fs", seconds, func=logging.warning)
            time.sleep(seconds)

    return True


def _before_sleep_log():
    logger = logging.root
    logger_log = logger.log

    def extensive_log(level, msg, *args, **kwargs):
        logger_log(level, msg, *args, **kwargs)
        if DEBUG_ON:
            logging.debug(str(msg) % args)

    # Monkeypatch inner logging function so it produces an exhaustive log when
    # used under the before-sleep logging utility in `tenacity`.
    logger.log = extensive_log
    return before_sleep_log(logger, logging.DEBUG, exc_info=True)


class RequestsHTTPError(HTTPError):
    """Custom `requests` HTTP error with status code and message."""

    def __init__(
        self, *args, status_code: int = 0, status_message: str = "Error", **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.status_code = status_code
        self.status_message = status_message


class Requests:
    """Wrapper over `requests` 3rd-party with error handling and retrying support."""

    def __init__(self, route_prefix: str, default_headers: Optional[dict] = None):
        self._route_prefix = route_prefix
        self._default_headers = default_headers

    def handle_error(self, response: requests.Response):
        resp_status_code = response.status_code
        log_func = logging.critical if resp_status_code // 100 == 5 else logging.debug
        log_more(
            "API response: %s %r", resp_status_code, response.reason, func=log_func
        )
        if response.ok:
            return

        fields = {}
        try:
            fields = response.json()
            while not isinstance(fields, dict):
                # For some reason we might still get a string from the deserialized
                # retrieved JSON payload. If a dictionary couldn't be obtained at all,
                # it will end up raising `RequestsHTTPError`.
                fields = json.loads(fields)
        except (JSONDecodeError, ValueError, TypeError):
            # No `fields` dictionary can be obtained at all.
            log_more("No fields were returned by the server", func=logging.critical)
            try:
                response.raise_for_status()
            except Exception as exc:  # pylint: disable=broad-except
                log_more(exc, func=logging.exception)
                raise RequestsHTTPError(exc, status_code=resp_status_code) from exc

        err_status_code = 0
        status_message = "Error"
        try:
            err_status_code = int(fields.get("status", resp_status_code))
            status_message = fields.get("error", {}).get("code", "Error")
            reason = fields.get("message") or fields.get("error", {}).get(
                "message", response.reason
            )
            raise HTTPError(f"{err_status_code} {status_message}: {reason}")
        except Exception as exc:  # pylint: disable=broad-except
            log_more(exc, func=logging.exception)
            raise RequestsHTTPError(
                str(fields), status_code=err_status_code, status_message=status_message
            ) from exc

    @retry(
        # Retry until either succeed or trying for the fifth time and still failing.
        # So sleep and retry for 4 times at most.
        stop=stop_after_attempt(5),
        # If the exception is no worth retrying or the number of tries is depleted,
        # then re-raise the last raised exception.
        reraise=True,
        # Decide if the raised exception needs retrying or not.
        retry=retry_if_exception(_needs_retry),
        # Produce debugging logging prior to each time we sleep & re-try.
        before_sleep=_before_sleep_log(),
        # Sleep between the tries with a random float amount of seconds like so:
        # 1. [0, 2]
        # 2. [0, 4]
        # 3. [0, 5]
        # 4. [0, 5]
        wait=wait_random_exponential(multiplier=2, max=5),
    )
    def _request(
        self,
        verb: Callable[..., requests.Response],
        url: str,
        *args,
        _handle_error: Optional[Callable[[requests.Response], None]] = None,
        _sensitive: bool = False,
        headers: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        # Absolute URLs override the prefix, so they are safe to be sent as they'll be
        # the same after joining.
        url = urlparse.urljoin(self._route_prefix, url)
        headers = headers if headers is not None else self._default_headers
        handle_error = _handle_error or self.handle_error

        url_for_log = url
        if _sensitive:
            # Omit query from the URL since might contain sensitive info.
            split = urlparse.urlsplit(url_for_log)
            url_for_log = urlparse.urlunsplit(
                [split.scheme, split.netloc, split.path, "", split.fragment]
            )
        log_more("%s %r", verb.__name__.upper(), url_for_log)
        response = verb(url, *args, headers=headers, **kwargs)
        handle_error(response)
        return response

    # CREATE
    def post(self, *args, **kwargs) -> requests.Response:
        return self._request(requests.post, *args, **kwargs)

    # RETRIEVE
    def get(self, *args, **kwargs) -> requests.Response:
        return self._request(requests.get, *args, **kwargs)

    # UPDATE
    def put(self, *args, **kwargs) -> requests.Response:
        return self._request(requests.put, *args, **kwargs)

    # DELETE
    def delete(self, *args, **kwargs) -> requests.Response:
        return self._request(requests.delete, *args, **kwargs)


def get_part_filename(msg: Message) -> Optional[str]:
    filename = msg.get_filename()
    if not filename:
        return None

    decoded = decode_header(filename)
    if decoded[0][1] is not None:
        filename = decoded[0][0].decode(decoded[0][1])
    return filename.replace("\r", "").replace("\n", "")


def get_decoded_email_body(message, html_first: bool = False) -> Tuple[str, bool]:
    """Decodes email body and extracts its text/html content.

    Automatically detects character set if the header is not set.

    Args:
        message: Raw 7-bit message body input e.g. from `imaplib`. Double encoded in quoted-printable and latin-1
        html_first: Prioritize html extraction over text when this is True
    Returns:
        (Tuple[str, bool]): Message body as unicode string and a boolean telling if the message has attachments

    """
    if not message.is_multipart():
        content_charset = message.get_content_charset()
        text = str(
            message.get_payload(decode=True),
            content_charset or ENCODING,
            "ignore",
        )
        return text.strip(), False

    text = html = None
    has_attachments = False

    for part in message.walk():
        if not part:
            continue
        content_filename = get_part_filename(part)
        if content_filename:
            has_attachments = True
            continue
        content_type = "text/plain"
        _data = ""
        content_charset = part.get_content_charset()
        if content_charset:
            content_type = part.get_content_type()
        payload = part.get_payload(decode=True)
        if payload:
            _data = str(payload, str(content_charset), "ignore")

        if content_type == "text/plain":
            text = _data
        elif content_type == "text/html":
            html = _data

    if html_first:
        data = html or text
    else:
        data = text or html
    data = data.strip() if data else ""
    return data, has_attachments
