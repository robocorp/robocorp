import logging
import os
import sys
import urllib.parse as urlparse
from functools import lru_cache
from typing import Dict, Optional

from ._requests import Requests, RequestsHTTPError

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


LOGGER = logging.getLogger(__name__)

AssetMeta = Dict[str, str]
Payload = TypedDict(
    "Payload",
    {
        "type": str,
        "content_type": Optional[str],
        "url": Optional[str],
    },
)
Asset = TypedDict(
    "Asset",
    {
        "id": str,
        "name": str,
        "payload": Payload,
    },
)


class AssetNotFound(RequestsHTTPError):
    """No asset with given name/id found."""


class AssetUploadFailed(RuntimeError):
    """There was an unexpected error while uploading an asset."""


def _url_join(*parts: str) -> str:
    """Join parts into a URL and handle missing/duplicate slashes."""
    url = ""
    for part in parts:
        url = urlparse.urljoin(url, part.strip("/") + "/")
    return url


def _get_endpoint() -> str:
    if endpoint := os.getenv("RC_API_URL_V1"):
        return endpoint

    # Note (2023-06-28):
    # While Control Room does set RC_API_URL_V1, this is not currently supported
    # in local development. We can use as fallback the Vault endpoint, but we
    # need to replace some parts to get the correct value. Examples:
    #   api.eu1.robocloud.eu -> api.eu1.robocorp.com/v1
    #   api.ci.robocloud.dev -> api.ci.robocorp.dev/v1
    #   api.eu2.robocorp.com -> api.eu2.robocorp.com/v1
    #   api.us1.robocorp.com -> api.us1.robocorp.com/v1
    LOGGER.info("Missing environment variable 'RC_API_URL_V1', attempting fallback")
    endpoint = os.getenv("RC_API_SECRET_HOST")
    if endpoint is None:
        raise RuntimeError("Missing environment variable 'RC_API_URL_V1'")

    if "robocloud.eu" in endpoint:
        endpoint = endpoint.replace("robocloud.eu", "robocorp.com")
    elif "robocloud.dev" in endpoint:
        endpoint = endpoint.replace("robocloud.dev", "robocorp.dev")

    if not endpoint.endswith("v1"):
        endpoint = _url_join(endpoint, "v1")

    return endpoint


def _get_token() -> str:
    if token := os.getenv("RC_API_TOKEN_V1"):
        return f"Bearer {token}"

    # Should we support this?
    if token := os.getenv("RC_API_KEY"):
        return f"RC-WSKEY {token}"

    # Note (2023-06-28):
    # While Control Room does set RC_API_TOKEN_V1, this is not currently
    # supported in local development. We can use as fallback the Vault token
    # which is identical.
    LOGGER.info("Missing environment variable 'RC_API_TOKEN_V1', attempting fallback")
    if token := os.getenv("RC_API_SECRET_TOKEN"):
        return f"Bearer {token}"

    raise RuntimeError("Missing environment variable 'RC_API_TOKEN_V1'")


@lru_cache(maxsize=1)
def get_assets_client():
    """
    Creates and returns an Asset Storage API client based on the injected
    environemnt variables from Control Room (or RCC).
    """
    try:
        workspace_id = os.environ["RC_WORKSPACE_ID"]
    except KeyError as err:
        raise RuntimeError("Missing environment variable 'RC_WORKSPACE_ID'") from err

    api_endpoint = _get_endpoint()
    api_token = _get_token()

    default_headers = {
        "Authorization": api_token,
        "Content-Type": "application/json",
    }

    route_prefix = _url_join(api_endpoint, "workspaces", workspace_id, "assets")
    assets_client = Requests(route_prefix, default_headers=default_headers)
    return assets_client
