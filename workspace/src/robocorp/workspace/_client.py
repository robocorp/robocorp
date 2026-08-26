from functools import lru_cache

from robocorp.workspace import ApiClient, Configuration


CONFIG = {
    "endpoint": None,
    "api_key": None,
    "workspace": None,
}


@lru_cache(maxsize=1)
def _get_configuration(**conf) -> Configuration:
    from ._environment import get_endpoint, get_token, get_workspace

    endpoint = conf["endpoint"] or get_endpoint()
    if api_key := conf["api_key"]:
        api_key_prefix = "RC-WSKEY"
    else:
        api_key = get_token()
        api_key_prefix = "Bearer"

    identifier = "API Key with permissions"
    configuration = Configuration(host=endpoint, api_key={identifier: api_key}, api_key_prefix={identifier: api_key_prefix})
    configuration.workspace = conf["workspace"] or get_workspace()
    return configuration


@lru_cache(maxsize=1)
def _get_client(configuration: Configuration) -> ApiClient:
    return ApiClient(configuration)


def get_configured_client() -> ApiClient:
    """Creates and returns a generic API client based on the injected environment
    variables from Control Room (or RCC) in the absence of an explicit configuration.
    """
    configuration = _get_configuration(**CONFIG)
    return _get_client(configuration)


def configure(**kwargs):
    """May be called at any time in order to (re)configure the API client settings.

    Args:
        endpoint: Specify a custom endpoint in the form of
            "https://cloud.robocorp.com/api/v1/".
        api_key: Provide an API key for the client to work with. When this is null, a
            token will be used instead (internal usage).
        workspace: The selected workspace ID whose resources will be interacted with.

    Note:
        In the absence of such an explicit configuration, the endpoint, credentials and
        workspace will be collected from the environment variables. These are usually
        injected by Control Room (or RCC) and are designed for internal usage only. So
        it's advised to run this configuration once with your preferred settings.
    """
    for key, value in kwargs.items():
        CONFIG[key] = value
