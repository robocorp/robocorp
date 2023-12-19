from concurrent import futures
from typing import Callable, TypeVar

T = TypeVar("T")


def run_in_thread(target: Callable[[], T], **kwargs) -> futures.Future[T]:
    """
    Runs a given target in a thread returning a Future which can be used to
    track its result.
    """
    fut: futures.Future[T] = futures.Future()
    if "name" not in kwargs:
        kwargs["name"] = f"run_in_thread:{target}"

    def new_target():
        try:
            result = target()
        except BaseException as e:
            fut.set_exception(e)
        else:
            fut.set_result(result)

    import threading

    t = threading.Thread(target=new_target, **kwargs)
    t.start()
    return fut
