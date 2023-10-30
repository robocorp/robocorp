"""Control Room Workspace Process API wrapper & library."""

from typing import Optional

from ._client import get_configured_client
from .api.process_api import ProcessApi
from .api.process_run_api import ProcessRunApi
from .models.list_processes200_response import ListProcesses200Response


def get_process_api_instance() -> ProcessApi:
    return ProcessApi(get_configured_client())


def get_process_run_api_instance() -> ProcessRunApi:
    return ProcessRunApi(get_configured_client())


def list_processes(limit: Optional[int] = None) -> ListProcesses200Response:
    # FIXME(cmin764, 30 Oct 2023): Auto-inject the Workspace ID from configuration
    #  through the templates. (so we'd eliminate this wrapper)
    from ._client import CONFIG, _get_configuration
    configuration = _get_configuration(CONFIG)
    return get_process_api_instance().list_processes(configuration.workspace, limit=limit)
