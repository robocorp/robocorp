from typing import Tuple, List
import sys
import threading

from ._config import BaseConfig
from ._logger_instances import _get_logger_instances
from .protocols import OptExcInfo, Status

from robo_log import critical


class OnExitContextManager:
    def __init__(self, on_exit):
        self.on_exit = on_exit

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.on_exit()


def register_auto_logging_callbacks(rewrite_hook_config: BaseConfig):
    # Make sure that this method should be called only once.
    registered = getattr(register_auto_logging_callbacks, "registered", False)
    if registered:
        import warnings

        warnings.warn("Auto logging is already setup. 2nd call has no effect.")
        return OnExitContextManager(lambda: None)
    register_auto_logging_callbacks.registered = True  # type: ignore

    tid = threading.get_ident()

    from ._rewrite_importhook import RewriteHook
    from ._lifecycle_hooks import (
        before_method,
        after_method,
        method_return,
        method_except,
    )

    hook = RewriteHook(rewrite_hook_config)
    sys.meta_path.insert(0, hook)

    status_stack = []

    def call_before_method(
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        args_dict: dict,
    ) -> None:
        from robo_log._obj_info_repr import get_obj_type_and_repr

        if tid != threading.get_ident():
            return

        status_stack.append([mod_name, name, "PASS"])
        args: List[Tuple[str, str, str]] = []
        for key, val in args_dict.items():
            for p in ("password", "passwd"):
                if p in key:
                    for robo_logger in _get_logger_instances():
                        robo_logger.hide_from_output(val)
                    break

            obj_type, obj_repr = get_obj_type_and_repr(val)
            args.append((f"{key}", obj_type, obj_repr))

        for robo_logger in _get_logger_instances():
            robo_logger.start_element(
                name,
                mod_name,
                filename,
                lineno,
                "METHOD",
                "",
                args,
                [],
            )

    def call_after_method(mod_name: str, filename: str, name: str, lineno: int) -> None:
        if tid != threading.get_ident():
            return

        try:
            pop_mod_name, pop_name, status = status_stack.pop(-1)
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            critical("On method return the status_stack was empty.")
            return
        else:
            if pop_mod_name != mod_name or pop_name != name:
                critical(
                    f"On method return status stack package/name was: {pop_mod_name}.{pop_name}. Received: {mod_name}.{name}."
                )
                return

        for robo_logger in _get_logger_instances():
            robo_logger.end_method(name, mod_name, status, [])

    def call_on_method_except(
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        exc_info: OptExcInfo,
    ) -> None:
        if tid != threading.get_ident():
            return

        try:
            pop_modname, pop_name, _curr_status = status_stack[-1]
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            critical("On method except the status_stack was empty.")
            return

        status_stack[-1][2] = Status.ERROR

        for robo_logger in _get_logger_instances():
            robo_logger.log_method_except(exc_info, unhandled=False)

    before_method.register(call_before_method)
    after_method.register(call_after_method)
    method_except.register(call_on_method_except)

    def _exit():
        # If the user actually used the with ... statement we'll remove things now.
        # Note: this is meant only for testing as it has caveats (mainly, modules
        # already loaded won't be rewritten and will have the hooks based on
        # the config which was set when it was loaded).
        sys.meta_path.remove(hook)
        before_method.unregister(call_before_method)
        after_method.unregister(call_after_method)
        register_auto_logging_callbacks.registered = False

    return OnExitContextManager(_exit)
