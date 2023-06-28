import logging
import sys
from functools import lru_cache
from typing import Dict, Optional

from ._requests import Requests, RequestsHTTPError
from ._utils import RequiresEnv, url_join

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


@lru_cache(maxsize=1)
def get_assets_client():
    """Creates and returns an API client based on the injected env vars in CR."""
    
    # CR is using new env. variables that are not known by RCC so not set to the env.
    # We need RC_API_URL_V1 and RC_API_KEY to be set

    # RC_API_KEY we can set to a value that is in the environment already RC_API_SECRET_TOKEN
    # - This is the same token

    # For RC_API_URL_V1 we need to do some tricks to get the correct url
    # We have RC_API_SECRET_HOST in the environment, but that needs some substring replacements:
    
    # OLD                  -> NEW
    # api.eu1.robocloud.eu -> api.eu1.robocorp.com/v1
    # api.ci.robocloud.dev -> api.ci.robocorp.dev/v1
    # api.eu2.robocorp.com -> api.eu2.robocorp.com/v1
    # api.us1.robocorp.com -> api.us1.robocorp.com/v1

    # RC_API_URL_V1 = RC_API_SECRET_HOST + "replace part"
    # RC_API_KEY = RC_API_SECRET_TOKEN

    requires_env = RequiresEnv(
        "Asset Storage feature can be used with Control Room only"
    )
    api_url = requires_env("RC_API_URL_V1")
    workspace_id = requires_env("RC_WORKSPACE_ID")
    api_token = requires_env("RC_API_TOKEN_V1", "")  # production availability
    api_key = requires_env("RC_API_KEY", "")  # for local tests only

    if not any([api_token, api_key]):
        raise RuntimeError("API token or key missing")
    auth_header = f"Bearer {api_token}" if api_token else f"RC-WSKEY {api_key}"
    default_headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }
    route_prefix = url_join(api_url, "workspaces", workspace_id, "assets")
    assets_client = Requests(route_prefix, default_headers=default_headers)
    return assets_client
