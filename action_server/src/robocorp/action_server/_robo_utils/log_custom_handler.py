import logging
from contextlib import contextmanager


class CustomHandler(logging.Handler):
    def __init__(self, level=logging.DEBUG):
        from . import callback

        super().__init__(level)
        self.on_record = callback.Callback()

    def emit(self, record):
        # Define the behavior to handle log records here
        self.on_record(record)


@contextmanager
def add_handler_callback(logger, on_log_emit, level=None):
    """
    Utility to add a handler in a context and remove it afterwards.
    """
    custom_handler = CustomHandler(level if level is not None else logging.DEBUG)
    with custom_handler.on_record.register(on_log_emit):
        initial_level = None
        if level is not None:
            initial_level = logger.level
            logger.setLevel(level)
        logger.addHandler(custom_handler)
        try:
            yield
        finally:
            logger.removeHandler(custom_handler)
            if initial_level is not None:
                logger.setLevel(initial_level)
