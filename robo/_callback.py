from logging import getLogger

logger = getLogger(__name__)


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
