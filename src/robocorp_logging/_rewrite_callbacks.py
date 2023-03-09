import traceback


class Callback(object):
    """
    Note that it's thread safe to register/unregister callbacks while callbacks
    are being notified, but it's not thread-safe to register/unregister at the
    same time in multiple threads.
    """

    def __init__(self):
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
                traceback.print_exc()


# Called as: before_method(__package__, filename, name, lineno, args_dict)
before_method = Callback()

# Called as: after_method(__package__, filename, name, lineno)
after_method = Callback()

# Called as: method_return(__package__, filename, name, lineno, return_value)
method_return = Callback()
