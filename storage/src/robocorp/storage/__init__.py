import logging
import time

from ._requests import RequestsHTTPError
from ._storage import get_assets_client


__version__ = "0.1.0"
version_info = [int(x) for x in __version__.split(".")]

LOGGER = logging.getLogger(__name__)
ASSETS_CLIENT = get_assets_client()


def list_assets():
    return ASSETS_CLIENT.get("").json()


def _retrieve_asset_id(name):
    for asset in list_assets():
        if asset["name"] == name:
            return asset["id"]


def _get_asset(name):
    asset_id = _retrieve_asset_id(name) or name
    try:
        return ASSETS_CLIENT.get(asset_id).json()
    except RequestsHTTPError as exc:
        if exc.status_code == 404:
            return None
        raise


def get_asset(name):
    data = _get_asset(name)
    payload = data["payload"]
    if payload["type"] == "empty":
        return ""

    url = payload["url"]
    return ASSETS_CLIENT.get(url, headers={}).text


def _create_asset(name):
    body = {"name": name}
    return ASSETS_CLIENT.post("", json=body).json()


def set_asset(name, value, block=True):
    existing_asset = _get_asset(name)
    if existing_asset:
        asset_id = existing_asset["id"]
    else:
        asset_id = _create_asset(name)["id"]

    body = {"content_type": "text/plain"}
    upload_data = ASSETS_CLIENT.post(f"{asset_id}/upload", json=body).json()
    ASSETS_CLIENT.put(upload_data["upload_url"], data=value, headers={})

    if block:
        upload_id = upload_data["id"]
        while True:
            upload_data = ASSETS_CLIENT.get(f"{asset_id}/uploads/{upload_id}").json()
            status = upload_data["status"]
            if status == "pending":
                time.sleep(1)
                continue
            elif status == "completed":
                break
            elif status == "failed":
                raise ValueError(upload_data["reason"])
            else:
                raise TypeError(f"invalid status {status!r}")


def delete_asset(name):
    ASSETS_CLIENT.delete(_get_asset(name)["id"])


__all__ = [
    "list_assets",
    "get_asset",
    "set_asset",
    "delete_asset",
]
