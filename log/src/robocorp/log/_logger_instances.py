# --- Private API
import threading
import typing
from contextlib import contextmanager
from typing import Dict, Iterator

if typing.TYPE_CHECKING:
    from ._robo_logger import _RoboLogger

_instances_lock = threading.RLock()
instances: Dict["_RoboLogger", int] = {}

_main_thread_id = threading.get_ident()


# We could use a set, but we're using a dict to keep the order.
@contextmanager
def _get_logger_instances(
    only_from_main_thread: bool = True,
) -> Iterator[Dict["_RoboLogger", int]]:
    """
    Args:
        only_from_main_thread:
            If true the logger instances will only be provided if this is the
            main thread.
            If false the logger instances will be provided even if not currently
            in the main thread.

    Returns:
        The logger instances registered so far. Note that a lock is held when
        the instances are requested and it's only released when the context
        exits.
    """
    if only_from_main_thread:
        if _main_thread_id != threading.get_ident():
            yield {}
            return

    with _instances_lock:
        yield instances
