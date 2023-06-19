import logging
from functools import lru_cache
from typing import Dict, Optional, TypedDict

from ._requests import Requests
from ._utils import RequiresEnv, url_join

LOGGER = logging.getLogger(__name__)


AssetMeta = Dict[str, str]
Payload = TypedDict(
    "Payload", {"type": str, "content_type": Optional[str], "url": Optional[str]}
)
Asset = TypedDict(
    "Asset",
    {
        "id": str,
        "name": str,
        "payload": Payload,
    },
)


class AssetNotFound(KeyError):
    """Raised when the queried asset couldn't be found."""


@lru_cache(maxsize=1)
def get_assets_client():
    """Creates and returns an API client based on the injected env vars in CR."""
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
