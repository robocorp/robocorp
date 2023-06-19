import logging
import random
import time
from typing import List, Optional, cast

from ._requests import RequestsHTTPError
from ._storage import Asset, AssetMeta, AssetNotFound
from ._storage import get_assets_client as _get_assets_client

__version__ = "0.1.0"
version_info = [int(x) for x in __version__.split(".")]

LOGGER = logging.getLogger(__name__)


def list_assets() -> List[AssetMeta]:
    """List all the existing assets.

    Returns:
        A list of assets where each asset is a dictionary with fields like 'id' and
        'name'.
    """
    assets_client = _get_assets_client()
    assets = assets_client.get("").json()
    LOGGER.info("Found %d assets.", len(assets))
    return assets


def _retrieve_asset_id(name: str) -> str:
    for asset in list_assets():
        if asset["name"] == name:
            asset_id = asset["id"]
            LOGGER.debug("Found existing asset %r with ID: %s", name, asset_id)
            return asset_id

    LOGGER.warning("No asset with name %r found, assuming ID.", name)
    return name


def _get_asset(name: str, raise_if_missing: bool = True) -> Optional[Asset]:
    assets_client = _get_assets_client()
    asset_id = _retrieve_asset_id(name)
    exception = None

    def _handle_error(resp):
        # NOTE(cmin764): The API will return 404 if the asset can't be found on the
        #  server, therefore don't let this raise, nor retry given this custom handler.
        nonlocal exception
        try:
            assets_client.handle_error(resp)
        except RequestsHTTPError as exc:
            if exc.status_code == 404:
                exception = exc
            else:
                raise

    LOGGER.debug("Retrieving asset %r with resulted ID %r.", name, asset_id)
    response = assets_client.get(asset_id, _handle_error=_handle_error)
    if response.ok:
        return cast(Asset, response.json())

    message = f"asset with name {name!r} and resulted ID {asset_id!r} couldn't be found"
    if raise_if_missing:
        raise AssetNotFound(message) from exception

    LOGGER.warning("%s%s!", message[0].upper(), message[1:])
    return None


def get_asset(name: str) -> str:
    """Get the asset's value by providing its `name`.

    Args:
        name: Name of the asset to fetch.

    Returns:
        The previously set value of this asset. (empty if it was never set)

    Raises:
        AssetNotFound: When the queried asset doesn't exist.
    """
    LOGGER.info("Retrieving asset %r.", name)
    payload = _get_asset(name)["payload"]  # type: ignore
    if payload["type"] == "empty":
        LOGGER.warning("Asset %r has no value set!", name)
        return ""

    assets_client = _get_assets_client()
    url = payload["url"]
    return assets_client.get(url, headers={}).text


def _create_asset(name: str):
    LOGGER.debug("Creating new asset with name %r.", name)
    assets_client = _get_assets_client()
    body = {"name": name}
    return assets_client.post("", json=body).json()


def set_asset(name: str, value: str, wait: bool = True):
    """Sets/Creates an asset named `name` with the provided `value`.

    Args:
        name: Name of the existing or new asset to create. (if missing)
        value: The new value set within the asset.
        wait: Blocks until the new value is reflected within the asset.

    Raises:
        AssetNotFound: When the queried asset doesn't exist.
    """
    existing_asset = _get_asset(name, raise_if_missing=False)
    if existing_asset:
        asset_id = existing_asset["id"]
        LOGGER.debug("Updating already existing asset with ID %r.", asset_id)
    else:
        asset_id = _create_asset(name)["id"]
        LOGGER.debug("Updating newly created asset with ID %r.", asset_id)

    assets_client = _get_assets_client()
    body = {"content_type": "text/plain"}
    upload_data = assets_client.post(f"{asset_id}/upload", json=body).json()
    assets_client.put(upload_data["upload_url"], data=value, headers={})

    if wait:
        LOGGER.info(
            "Waiting for the sent value to be set successfully in the %r asset...", name
        )
        upload_url = f"{asset_id}/uploads/{upload_data['id']}"
        while True:
            upload_data = assets_client.get(upload_url).json()
            status = upload_data["status"]
            if status == "pending":
                sleep_time = round(random.uniform(0, 1), 2)
                LOGGER.debug("Asset upload still pending, sleeping %.2f...", sleep_time)
                time.sleep(sleep_time)
                continue
            elif status == "completed":
                break
            elif status == "failed":
                raise ValueError(
                    f"asset {name!r} upload failed with {upload_data['reason']!r}"
                )
            else:
                raise TypeError(f"asset {name!r} got invalid status {status!r}")

    LOGGER.info("Asset with name %r set successfully.", name)


def delete_asset(name: str):
    """Delete an asset by providing its `name`.

    Args:
        name: Name of the asset to delete.

    Raises:
        AssetNotFound: When the queried asset doesn't exist.
    """
    LOGGER.info("Deleting asset %r.", name)
    assets_client = _get_assets_client()
    assets_client.delete(_get_asset(name)["id"])  # type: ignore


__all__ = [
    "AssetNotFound",
    "list_assets",
    "get_asset",
    "set_asset",
    "delete_asset",
]
