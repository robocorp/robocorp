import sys
import threading
from robo_log.protocols import OptExcInfo
from robo_log._logger_instances import _get_logger_instances
from robo_log import critical
from .protocols import Status


class OnExitContextManager:
    def __init__(self, on_exit):
        self.on_exit = on_exit

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.on_exit()


def register_auto_logging_callbacks(rewrite_hook_config):
    # Make sure that this method should be called only once.
    registered = getattr(register_auto_logging_callbacks, "registered", False)
    if registered:
        import warnings

        warnings.warn("Auto logging is already setup. 2nd call has no effect.")
        return OnExitContextManager(lambda: None)
    register_auto_logging_callbacks.registered = True

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
        package: str,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        args_dict: dict,
    ) -> None:
        if tid != threading.get_ident():
            return

        status_stack.append([package, name, "PASS"])
        args = []
        for key, val in args_dict.items():
            for p in ("password", "passwd"):
                if p in key:
                    for robo_logger in _get_logger_instances():
                        robo_logger.hide_from_output(val)
                    break

            args.append((f"{key}", f"{val!r}"))
        for robo_logger in _get_logger_instances():
            robo_logger.start_element(
                name,
                f"{package}.{mod_name}",
                filename,
                lineno,
                "METHOD",
                "",
                args,
                [],
                [],
            )

    def call_after_method(
        package: str, mod_name: str, filename: str, name: str, lineno: int
    ) -> None:
        if tid != threading.get_ident():
            return

        try:
            pop_package, pop_name, status = status_stack.pop(-1)
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            critical("On method return the status_stack was empty.")
            return
        else:
            if pop_package != package or pop_name != name:
                critical(
                    f"On method return status stack package/name was: {pop_package}.{pop_name}. Received: {package}.{name}."
                )
                return

        for robo_logger in _get_logger_instances():
            robo_logger.end_method(name, f"{package}.{mod_name}", status, [])

    def call_on_method_except(
        package: str,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        exc_info: OptExcInfo,
    ) -> None:
        if tid != threading.get_ident():
            return

        try:
            pop_package, pop_name, _curr_status = status_stack[-1]
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            critical("On method except the status_stack was empty.")
            return

        if pop_package != package or pop_name != name:
            critical(
                f"On method except status stack package/name was: {pop_package}.{pop_name}. Received: {package}.{name}."
            )
            return
        status_stack[-1][2] = Status.ERROR

        for robo_logger in _get_logger_instances():
            robo_logger.log_method_except(
                f"{package}.{mod_name}", filename, name, lineno, exc_info, False
            )

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
