import logging
from typing import Dict, Optional

import uvicorn
from fastapi.staticfiles import StaticFiles

log = logging.getLogger(__name__)


def _name_as_summary(name):
    return name.replace("_", " ").title()


def _name_to_url(name):
    return name.replace("_", "-")


def start_server() -> None:
    import docstring_parser

    from . import _actions_run
    from ._api_run import run_api_router
    from ._app import get_app
    from ._models import Action, ActionPackage, get_db
    from ._settings import get_settings

    settings = get_settings()

    log.debug("Starting server (settings: %s)", settings)

    def _on_startup():
        log.info("Documentation in /docs")

    def _on_shutdown():
        pass

    app = get_app()
    app.add_event_handler("startup", _on_startup)
    app.add_event_handler("shutdown", _on_shutdown)

    artifacts_dir = settings.artifacts_dir

    app.mount(
        "/artifacts",
        StaticFiles(directory=artifacts_dir),
        name="artifacts",
    )
    # This has the nasty side-effect of not allowing further routes to work!
    # app.mount(
    #     "/",
    #     StaticFiles(packages=[("robocorp.action_server", "_static")], html=True),
    #     name="static",
    # )

    db = get_db()
    action: Action
    action_package_id_to_action_package: Dict[str, ActionPackage] = dict(
        (action_package.id, action_package) for action_package in db.all(ActionPackage)
    )

    for action in db.all(Action):
        doc_desc: Optional[str] = ""
        if action.docs:
            try:
                parsed = docstring_parser.parse(action.docs)
                doc_desc = parsed.long_description or parsed.short_description
            except Exception:
                log.exception("Error parsing docstring: %s", action.docs)
                doc_desc = str(action.docs or "")

        if not doc_desc:
            doc_desc = ""

        action_package = action_package_id_to_action_package.get(
            action.action_package_id
        )
        if not action_package:
            log.critical("Unable to find action package: %s", action.action_package_id)
            continue

        app.add_api_route(
            f"/api/actions/{_name_to_url(action_package.name)}/{_name_to_url(action.name)}/run",
            _actions_run.generate_func_from_action(action),
            name=action.name,
            summary=_name_as_summary(action.name),
            description=doc_desc,
            operation_id=action.name,
            methods=["POST"],
        )

    app.include_router(run_api_router)

    kwargs = settings.to_uvicorn()
    uvicorn.run(app, **kwargs)
