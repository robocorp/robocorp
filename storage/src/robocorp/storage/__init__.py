import logging

from ._storage import get_assets_client


__version__ = "0.1.0"
version_info = [int(x) for x in __version__.split(".")]

LOGGER = logging.getLogger(__name__)
ASSETS_CLIENT = get_assets_client()


def list_assets():
    response = ASSETS_CLIENT.get("")
    return response.json()


__all__ = [
    "list_assets",
]
