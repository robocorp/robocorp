from logging import getLogger

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
        self._callbacks = []

    def register(self, callback):
        new_callbacks = self._callbacks[:]
        new_callbacks.append(callback)
        self._callbacks = new_callbacks

        # Enable using as a context manager to automatically call the unregister.
        return _OnExitContextManager(lambda: self.unregister(callback))

    def unregister(self, callback):
        new_callbacks = [x for x in self._callbacks if x != callback]
        self._callbacks = new_callbacks

    def __call__(self, *args, **kwargs):
        for c in self._callbacks:
            try:
                c(*args, **kwargs)
            except:
                logger.exception("Error in callback.")
                if self.raise_exceptions:
                    raise


# Called as: before_method(__package__, __name__, filename, name, lineno, args_dict)
before_method = Callback()

# Called as: after_method(__package__, __name__, filename, name, lineno)
after_method = Callback()

# Called as: method_return(__package__, __name__, filename, name, lineno, return_value)
method_return = Callback()

# Called as: method_except(__package__, __name__, filename, name, lineno, exc_info)
# tp, e, tb = exc_info
method_except = Callback()


def iter_all_callbacks():
    yield before_method
    yield after_method
    yield method_return
    yield method_except
