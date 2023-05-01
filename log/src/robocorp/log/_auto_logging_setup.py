from robocorp.log import critical, is_sensitive_variable_name
from ._config import BaseConfig
from ._logger_instances import _get_logger_instances
from ._obj_info_repr import get_obj_type_and_repr
from .protocols import OptExcInfo, Status
import sys
import threading
from typing import Tuple, List, Any, Optional

from .protocols import LogElementType


class OnExitContextManager:
    def __init__(self, on_exit):
        self.on_exit = on_exit

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.on_exit()


def _get_obj_type_and_repr_and_hide_if_needed(key, val):
    obj_type, obj_repr = get_obj_type_and_repr(val)

    if is_sensitive_variable_name(key):
        for robo_logger in _get_logger_instances():
            robo_logger.hide_from_output(obj_repr)
            if isinstance(val, str):
                robo_logger.hide_from_output(val)
    return obj_type, obj_repr


class _StackEntry:
    __slots__ = "mod_name name status".split()

    def __init__(self, mod_name, name, status):
        self.mod_name = mod_name
        self.name = name
        self.status = status


class _AutoLogging:
    """
    Class responsible for listening for callbacks and then dispatching those
    to the logger.
    """

    def __init__(self, rewrite_hook_config: BaseConfig) -> None:
        from ._rewrite_importhook import RewriteHook

        self.tid = threading.get_ident()
        self.status_stack: List[_StackEntry] = []
        self._rewrite_hook_config = rewrite_hook_config
        self._hook: Optional[RewriteHook] = None

    def register(self) -> None:
        from robocorp.log import _lifecycle_hooks
        from ._rewrite_importhook import RewriteHook

        for name, callback in _lifecycle_hooks.iter_all_name_and_callback():
            callback.register(getattr(self, f"call_{name}"))

        self._hook = hook = RewriteHook(self._rewrite_hook_config)
        sys.meta_path.insert(0, hook)

    def unregister(self) -> None:
        from robocorp.log import _lifecycle_hooks

        for name, callback in _lifecycle_hooks.iter_all_name_and_callback():
            callback.unregister(getattr(self, f"call_{name}"))

        assert self._hook
        sys.meta_path.remove(self._hook)
        self._hook = None

    def call_before_method(
        self,
        method_type: LogElementType,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        args_dict: dict,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        if method_type != "UNTRACKED_GENERATOR":
            # We don't change the stack for untracked generators
            # because we don't know when they may yield.
            self.status_stack.append(_StackEntry(mod_name, name, "PASS"))

        args: List[Tuple[str, str, str]] = []
        for key, val in args_dict.items():
            obj_type, obj_repr = _get_obj_type_and_repr_and_hide_if_needed(key, val)
            args.append((f"{key}", obj_type, obj_repr))

        for robo_logger in _get_logger_instances():
            robo_logger.start_element(
                name,
                mod_name,
                filename,
                lineno,
                method_type,
                "",
                args,
            )

    def call_after_method(
        self,
        method_type: LogElementType,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        status = "PASS"
        if method_type != "UNTRACKED_GENERATOR":
            try:
                pop_stack_entry = self.status_stack.pop(-1)
            except IndexError:
                # oops, something bad happened, the stack is unsynchronized
                critical("On method return the status_stack was empty.")
                return
            else:
                if pop_stack_entry.mod_name != mod_name or pop_stack_entry.name != name:
                    critical(
                        f"On method return status stack package/name was: {pop_stack_entry.mod_name}.{pop_stack_entry.name}. Received: {mod_name}.{name}."
                    )
                    return
            status = pop_stack_entry.status

        for robo_logger in _get_logger_instances():
            robo_logger.end_method(method_type, name, mod_name, status)

    def call_before_yield(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        yielded_value: Any,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        try:
            pop_stack_entry = self.status_stack.pop(-1)
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            critical("On before yield the status_stack was empty.")
            return
        else:
            if pop_stack_entry.mod_name != mod_name or pop_stack_entry.name != name:
                critical(
                    f"On before yield status stack package/name was: {pop_stack_entry.mod_name}.{pop_stack_entry.name}. Received: {mod_name}.{name}."
                )
                return

        yielded_value_type, yielded_value_repr = get_obj_type_and_repr(yielded_value)

        for robo_logger in _get_logger_instances():
            robo_logger.yield_suspend(
                name, mod_name, filename, lineno, yielded_value_type, yielded_value_repr
            )

    def call_after_yield(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        self.status_stack.append(_StackEntry(mod_name, name, "PASS"))

        for robo_logger in _get_logger_instances():
            robo_logger.yield_resume(name, mod_name, filename, lineno)

    def call_before_yield_from(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        try:
            pop_stack_entry = self.status_stack.pop(-1)
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            critical("On before yield from the status_stack was empty.")
            return
        else:
            if pop_stack_entry.mod_name != mod_name or pop_stack_entry.name != name:
                critical(
                    f"On before yield from status stack package/name was: {pop_stack_entry.mod_name}.{pop_stack_entry.name}. Received: {mod_name}.{name}."
                )
                return

        for robo_logger in _get_logger_instances():
            robo_logger.yield_from_suspend(name, mod_name, filename, lineno)

    def call_after_yield_from(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        self.status_stack.append(_StackEntry(mod_name, name, "PASS"))

        for robo_logger in _get_logger_instances():
            robo_logger.yield_from_resume(name, mod_name, filename, lineno)

    def call_after_assign(
        self,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        assign_name: str,
        assign_value: Any,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        assign_type, assign_repr = _get_obj_type_and_repr_and_hide_if_needed(
            assign_name, assign_value
        )

        for robo_logger in _get_logger_instances():
            robo_logger.after_assign(
                name, mod_name, filename, lineno, assign_name, assign_type, assign_repr
            )

    def call_method_return(self, *args, **kwargs):
        pass

    def call_method_except(
        self,
        method_type: LogElementType,
        mod_name: str,
        filename: str,
        name: str,
        lineno: int,
        exc_info: OptExcInfo,
    ) -> None:
        if self.tid != threading.get_ident():
            return

        if method_type == "UNTRACKED_GENERATOR":
            # TODO: Investigate: in this case maybe we should create a dummy
            # stack entry? -- Must verify how it'd look in the UI.
            pass

        try:
            _stack_entry = self.status_stack[-1]
        except IndexError:
            # oops, something bad happened, the stack is unsynchronized
            critical("On method except the status_stack was empty.")
            return

        self.status_stack[-1].status = Status.ERROR

        for robo_logger in _get_logger_instances():
            robo_logger.log_method_except(exc_info, unhandled=False)


def register_auto_logging_callbacks(rewrite_hook_config: BaseConfig):
    # Make sure that this method should be called only once.
    registered = getattr(register_auto_logging_callbacks, "registered", False)
    if registered:
        import warnings

        warnings.warn("Auto logging is already setup. 2nd call has no effect.")
        return OnExitContextManager(lambda: None)
    register_auto_logging_callbacks.registered = True  # type: ignore

    auto_logging = _AutoLogging(rewrite_hook_config)
    auto_logging.register()

    def _exit():
        # If the user actually used the with ... statement we'll remove things now.
        # Note: this is meant only for testing as it has caveats (mainly, modules
        # already loaded won't be rewritten and will have the hooks based on
        # the config which was set when it was loaded).
        auto_logging.unregister()
        register_auto_logging_callbacks.registered = False

    return OnExitContextManager(_exit)
