from functools import wraps


def _handle_decorator(func, suppress_contextmanager, variables=True, methods=True):
    @wraps(func)
    def new_func(*args, **kwargs):
        with suppress_contextmanager(variables, methods):
            return func(*args, **kwargs)

    return new_func


class _DecoratorOrCtx:
    def __init__(self, suppress_contextmanager, args, kwargs):
        self._suppress_contextmanager = suppress_contextmanager
        self._args = args
        self._kwargs = kwargs
        self._ctx = None

    def __enter__(self):
        # It was used in a with statement
        ctx = self._suppress_contextmanager(*self._args, **self._kwargs)
        self._ctx = ctx
        self._ctx.__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._ctx.__exit__(exc_type, exc_val, exc_tb)
        self._ctx = None

    def __call__(self, func):
        # It was used as a decorator with arguments
        return _handle_decorator(
            func, self._suppress_contextmanager, *self._args, **self._kwargs
        )


class SuppressHelper:
    """
    Helper class to help in dealing with case where suppress can be used
    either as a decorator (with or without arguments) or as a with statement.
    """

    def __init__(self, suppress_contextmanager):
        self._suppress_contextmanager = suppress_contextmanager

    def handle(self, *args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            # Used as decorator.
            # i.e.:
            #
            # from robocorp import log
            # @log.suppress
            # def func():
            #     ....
            func = args[0]
            decorator_or_ctx = _DecoratorOrCtx(
                self._suppress_contextmanager, args, kwargs
            )
            return decorator_or_ctx(func)

        return _DecoratorOrCtx(self._suppress_contextmanager, args, kwargs)
