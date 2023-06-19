import logging
import random
import time
from typing import Dict, List, Optional

from ._requests import RequestsHTTPError
from ._storage import AssetNotFound, get_assets_client


__version__ = "0.1.0"
version_info = [int(x) for x in __version__.split(".")]

LOGGER = logging.getLogger(__name__)
ASSETS_CLIENT = get_assets_client()


def list_assets() -> List[Dict]:
    assets = ASSETS_CLIENT.get("").json()
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


def _get_asset(name: str, raise_if_missing: bool = True) -> Optional[Dict]:
    asset_id = _retrieve_asset_id(name)
    exception = None

    def _handle_error(resp):
        # NOTE(cmin764): The API will return 404 if the asset can't be found on the
        #  server, therefore don't let this raise, nor retry given this custom handler.
        nonlocal exception
        try:
            ASSETS_CLIENT.handle_error(resp)
        except RequestsHTTPError as exc:
            if exc.status_code == 404:
                exception = exc
            else:
                raise

    LOGGER.debug("Retrieving asset %r with resulted ID %r.", name, asset_id)
    response = ASSETS_CLIENT.get(asset_id, _handle_error=_handle_error)
    if response.ok:
        return response.json()

    message = (
        f"asset with name {name!r} and resulted ID {asset_id!r} couldn't be found"
    )
    if raise_if_missing:
        raise AssetNotFound(message) from exception

    LOGGER.warning("%s%s!", message[0].upper(), message[1:])
    return None


def get_asset(name: str) -> str:
    LOGGER.info("Retrieving asset %r.", name)
    payload = _get_asset(name)["payload"]
    if payload["type"] == "empty":
        LOGGER.warning("Asset %r has no value set!", name)
        return ""

    url = payload["url"]
    return ASSETS_CLIENT.get(url, headers={}).text


def _create_asset(name):
    LOGGER.debug("Creating new asset with name %r.", name)
    body = {"name": name}
    return ASSETS_CLIENT.post("", json=body).json()


def set_asset(name: str, value: str, wait: bool = True):
    existing_asset = _get_asset(name, raise_if_missing=False)
    if existing_asset:
        asset_id = existing_asset["id"]
        LOGGER.debug("Updating already existing asset with ID %r.", asset_id)
    else:
        asset_id = _create_asset(name)["id"]
        LOGGER.debug("Updating newly created asset with ID %r.", asset_id)

    body = {"content_type": "text/plain"}
    upload_data = ASSETS_CLIENT.post(f"{asset_id}/upload", json=body).json()
    ASSETS_CLIENT.put(upload_data["upload_url"], data=value, headers={})

    if wait:
        LOGGER.info(
            "Waiting for the sent value to be set successfully in the %r asset...",
            name
        )
        upload_url = f"{asset_id}/uploads/{upload_data['id']}"
        while True:
            upload_data = ASSETS_CLIENT.get(upload_url).json()
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
    LOGGER.info("Deleting asset %r.", name)
    ASSETS_CLIENT.delete(_get_asset(name)["id"])


__all__ = [
    "list_assets",
    "get_asset",
    "set_asset",
    "delete_asset",
]
