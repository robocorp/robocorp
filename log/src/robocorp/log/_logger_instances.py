# --- Private API
import threading
from typing import Dict
import typing


if typing.TYPE_CHECKING:
    from ._robo_logger import _RoboLogger

__tlocal_log__ = threading.local()


# We could use a set, but we're using a dict to keep the order.
def _get_logger_instances() -> Dict["_RoboLogger", int]:
    instances: Dict["_RoboLogger", int]
    try:
        instances = __tlocal_log__.instances
    except AttributeError:
        instances = __tlocal_log__.instances = {}
    return instances
