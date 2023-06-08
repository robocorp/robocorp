import json
import logging
import os
import random
import time
import urllib.parse as urlparse
from typing import Callable, Optional

import requests
from requests.exceptions import HTTPError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)

LOGGER = logging.getLogger(__name__)
DEBUG = bool(os.getenv("RC_WORKITEM_DEBUG") or os.getenv("RPA_DEBUG_API"))


def _needs_retry(exc: BaseException) -> bool:
    # Don't retry on some specific error codes or messages.

    # https://www.restapitutorial.com/httpstatuscodes.html
    # 400 - payload is bad and needs to be changed
    # 401 - missing auth bearer token
    # 403 - auth is in place, but not allowed (insufficient privileges)
    # 409 - payload not good for the affected resource
    no_retry_codes = [400, 401, 403, 409]

    if isinstance(exc, RequestsHTTPError):
        if exc.status_code in no_retry_codes:
            return False

        if exc.status_code == 429:
            # We hit the rate limiter, so sleep extra.
            seconds = random.uniform(1, 3)
            LOGGER.warning("Rate limit hit, sleeping: %fs", seconds)
            time.sleep(seconds)

    return True


def _before_sleep_log():
    log_method = LOGGER.log

    def extensive_log(level, msg, *args, **kwargs):
        log_method(level, msg, *args, **kwargs)
        if DEBUG:
            LOGGER.debug(msg, *args)

    # Monkeypatch inner logging function so it produces an exhaustive log when
    # used under the before-sleep logging utility in `tenacity`.
    LOGGER.log = extensive_log
    return before_sleep_log(LOGGER, logging.DEBUG, exc_info=True)


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
        log_func = LOGGER.critical if resp_status_code // 100 == 5 else LOGGER.debug
        log_func("API response: %s %r", resp_status_code, response.reason)

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
        except (json.JSONDecodeError, ValueError, TypeError):
            # No `fields` dictionary can be obtained at all.
            LOGGER.critical("No fields were returned by the server")
            try:
                response.raise_for_status()
            except Exception as exc:
                LOGGER.exception(exc)
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
        except Exception as exc:
            LOGGER.exception(exc)
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

        LOGGER.debug("%s %r", verb.__name__.upper(), url_for_log)
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
