import functools
import sys


@functools.lru_cache  # Make sure that it's called only once
def _config_uiautomation():
    if sys.platform == "win32":
        # Configure comtypes to not generate DLL bindings into
        # current environment, instead keeping them in memory.
        # Slower, but prevents dirtying environments.
        import logging

        import comtypes.client

        from ._vendored.uiautomation.uiautomation import Logger

        comtypes.client.gen_dir = None

        # Prevent comtypes writing a lot of log messages.
        comtypes_logger = logging.getLogger("comtypes")
        comtypes_logger.propagate = False
        # Disable uiautomation writing into a log file.
        Logger.SetLogFile("")
