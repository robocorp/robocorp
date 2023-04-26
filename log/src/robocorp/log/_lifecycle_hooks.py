from logging import getLogger
from typing import Iterator, Tuple

logger = getLogger(__name__)


class _OnExitContextManager:
    def __init__(self, on_exit):
        self.on_exit = on_exit

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.on_exit()


class Callback(object):
    """
    Note that it's thread safe to register/unregister callbacks while callbacks
    are being notified, but it's not thread-safe to register/unregister at the
    same time in multiple threads.
    """

    def __init__(self):
        self.raise_exceptions = False
        self._callbacks = ()

    def register(self, callback):
        self._callbacks = self._callbacks + (callback,)

        # Enable using as a context manager to automatically call the unregister.
        return _OnExitContextManager(lambda: self.unregister(callback))

    def unregister(self, callback):
        self._callbacks = tuple(x for x in self._callbacks if x != callback)

    def __call__(self, *args, **kwargs):
        for c in self._callbacks:
            try:
                c(*args, **kwargs)
            except:
                logger.exception(f"Error calling: {c}.")
                if self.raise_exceptions:
                    raise


# Called as: before_method(__name__, filename, name, lineno, args_dict)
before_method = Callback()

# Called as: after_method(__name__, filename, name, lineno)
after_method = Callback()

# Called as: method_return(__name__, filename, name, lineno, return_value)
method_return = Callback()

# Called as: method_except(__name__, filename, name, lineno, exc_info)
# tp, e, tb = exc_info
method_except = Callback()

# Called as: after_assign(__name__, filename, name, lineno, assign_name, assign_value)
after_assign = Callback()

# Called as: before_yield(__name__, filename, name, lineno, yielded_value)
before_yield = Callback()

# Called as: after_yield(__name__, filename, name, lineno)
after_yield = Callback()

# Called as: before_yield_from(__name__, filename, name, lineno)
before_yield_from = Callback()

# Called as: after_yield_from(__name__, filename, name, lineno)
after_yield_from = Callback()


def iter_all_callbacks() -> Iterator[Callback]:
    for _key, val in globals().items():
        if isinstance(val, Callback):
            yield val


def iter_all_name_and_callback() -> Iterator[Tuple[str, Callback]]:
    for key, val in globals().items():
        if isinstance(val, Callback):
            yield (key, val)
