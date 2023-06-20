import logging
import random
import time
from typing import List, cast

from ._requests import RequestsHTTPError
from ._storage import Asset, AssetMeta, AssetNotFound, AssetUploadFailed
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
    LOGGER.debug("Retrieved %d assets", len(assets))
    return assets


def _retrieve_asset_id(name: str) -> str:
    for asset in list_assets():
        if asset["name"] == name:
            asset_id = asset["id"]
            LOGGER.debug("Found existing asset %r with id: %s", name, asset_id)
            return asset_id

    LOGGER.warning("No asset with name %r found, assuming id", name)
    return name


def _get_asset(name: str) -> Asset:
    assets_client = _get_assets_client()
    asset_id = _retrieve_asset_id(name)

    def _handle_error(resp):
        try:
            assets_client.handle_error(resp)
        except RequestsHTTPError as exc:
            if exc.status_code == 404:
                message = f"Asset {name!r} with id {asset_id!r} not found"
                raise AssetNotFound(message) from exc
            else:
                raise exc

    response = assets_client.get(asset_id, _handle_error=_handle_error)
    return cast(Asset, response.json())


def get_asset(name: str) -> str:
    """Get an asset's value by providing its `name`.

    Args:
        name: Name of the asset

    Returns:
        The previously set value of this asset, or empty string if not set

    Raises:
        AssetNotFound: Asset with given name does not exist
    """
    LOGGER.info("Retrieving asset: %r", name)
    payload = _get_asset(name)["payload"]
    if payload["type"] == "empty":
        LOGGER.warning("Asset %r has no value set", name)
        return ""

    assets_client = _get_assets_client()
    url = payload["url"]
    return assets_client.get(url, headers={}).text


def _create_asset(name: str) -> Asset:
    LOGGER.debug("Creating new asset with name: %r", name)
    assets_client = _get_assets_client()
    body = {"name": name}
    return assets_client.post("", json=body).json()


def set_asset(name: str, value: str, wait: bool = True):
    """Creates or updates an asset named `name` with the provided `value`.

    Args:
        name: Name of the existing or new asset to create (if missing)
        value: The new value set within the asset
        wait: Wait for value to be set succesfully

    Raises:
        AssetUploadFailed: Unexpected error while uploading asset
    """
    try:
        asset_id = _get_asset(name)["id"]
        LOGGER.debug("Updating existing asset with id: %r", asset_id)
    except AssetNotFound:
        asset_id = _create_asset(name)["id"]
        LOGGER.debug("Created new asset with id: %r", asset_id)

    assets_client = _get_assets_client()
    body = {"content_type": "text/plain"}
    upload_data = assets_client.post(f"{asset_id}/upload", json=body).json()
    assets_client.put(upload_data["upload_url"], data=value, headers={})

    if not wait:
        return

    LOGGER.info("Waiting for asset %r value to update succesfully", name)
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
            reason = upload_data["reason"]
            raise AssetUploadFailed(f"Asset {name!r} upload failed: {reason!r}")
        else:
            raise AssetUploadFailed(f"Asset {name!r} got invalid status: {status!r}")

    LOGGER.info("Asset %r set successfully", name)


def delete_asset(name: str):
    """Delete an asset by providing its `name`.

    Args:
        name: Name of the asset to delete

    Raises:
        AssetNotFound: Asset with given name does not exist
    """
    LOGGER.info("Deleting asset: %r", name)
    assets_client = _get_assets_client()
    assets_client.delete(_get_asset(name)["id"])


__all__ = [
    "AssetNotFound",
    "list_assets",
    "get_asset",
    "set_asset",
    "delete_asset",
]
