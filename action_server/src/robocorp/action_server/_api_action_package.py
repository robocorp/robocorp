from dataclasses import dataclass
from typing import List

from fastapi.routing import APIRouter

from robocorp.action_server._models import Action, ActionPackage

action_package_api_router = APIRouter(prefix="/api/actionPackages")


@dataclass
class ActionPackageApi:
    id: str  # primary key (uuid)
    name: str  # The name for the action package
    actions: List[Action]


@action_package_api_router.get("/", response_model=List[ActionPackageApi])
def list_action_packages():
    from robocorp.action_server._models import get_db

    db = get_db()
    with db.connect():
        # We're running in the threadpool used by fast api, so, we need
        # to make a new connection (maybe it'd make sense to create a
        # connection pool instead of always creating a new connection...).
        action_packages = db.all(ActionPackage)

        id_to_action_package = {}
        for action_package in action_packages:
            id_to_action_package[action_package.id] = ActionPackageApi(
                action_package.id, action_package.name, []
            )

        for action in db.all(Action):
            id_to_action_package[action.action_package_id].actions.append(action)

    return list(id_to_action_package.values())
