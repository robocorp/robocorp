import logging

from ._requests import Requests
from ._utils import RequiresEnv, url_join


LOGGER = logging.getLogger(__name__)


class AssetNotFound(KeyError):
    """Raised when the queried asset couldn't be found."""


def get_assets_client():
    """Creates and returns an API client based on the injected env vars in CR."""
    requires_env = RequiresEnv(
        "Asset Storage feature can be used with Control Room only"
    )
    api_url = requires_env("RC_API_URL_V1")
    workspace_id = requires_env("RC_WORKSPACE_ID")
    api_token = requires_env("RC_API_TOKEN_V1", "")  # production availability
    api_key = requires_env("RC_API_KEY", "")  # for local tests only

    route_prefix = url_join(api_url, "workspaces", workspace_id, "assets")
    assert any([api_token, api_key]), "API token or key missing"
    auth_header = f"Bearer {api_token}" if api_token else f"RC-WSKEY {api_key}"
    default_headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json",
    }
    assets_client = Requests(route_prefix, default_headers=default_headers)
    return assets_client
